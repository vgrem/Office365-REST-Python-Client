"""Offline tests for the document-library adapters.

Covers the verification enumeration: a target library always contains
SharePoint-owned scaffolding (``Forms/``, ``desktop.ini``) that the source
projection deliberately skips, so the target must skip it too or every migrated
library is reported as having "extra" content. On ``SiteAssets`` that scaffolding
also includes the site icon and the auto-provisioned ``<web title> Notebook``
folder. Also covers folder items — the source plans folders as first-class items,
so the target must create them instead of trying to upload a file named after the
folder.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from office365.migration.base import MigrationItem
from office365.migration.sharepoint.adapters import SharePointLibrarySource, SharePointLibraryTarget


class _Entry:
    def __init__(self, server_relative_url: str) -> None:
        self.server_relative_url = server_relative_url


class _Collection:
    def __init__(self, entries: list[_Entry]) -> None:
        self._entries = entries

    def execute_query(self) -> list[_Entry]:
        return self._entries


class _Request:
    def __init__(self, url: str, present: bool) -> None:
        self._url = url
        self._present = present

    def get(self) -> "_Request":
        return self

    def execute_query(self) -> "_Request":
        if not self._present:
            raise ValueError(f"not found: {self._url}")
        return self


class _Web:
    def __init__(self, folders=(), files=()) -> None:
        self._folders = set(folders)
        self._files = set(files)

    def get_folder_by_server_relative_url(self, url: str) -> _Request:
        return _Request(url, url in self._folders)

    def get_file_by_server_relative_url(self, url: str) -> _Request:
        return _Request(url, url in self._files)


class _SiteAssetsWeb(_Web):
    """A web whose title is available, so the notebook rule can be applied."""

    def __init__(self, title: str, folders=(), files=()) -> None:
        super().__init__(folders=folders, files=files)
        self.properties = {"Title": title}

    @property
    def title(self) -> str:
        return self.properties["Title"]


class _Context:
    def __init__(self, web: _Web | None = None) -> None:
        self.web = web or _Web()
        self.executed = 0

    def execute_query(self) -> None:
        self.executed += 1


class _TargetFolder:
    server_relative_url = "/sites/x/Docs"

    def __init__(self, files=(), folders=(), context: _Context | None = None) -> None:
        self._files = list(files)
        self._folders = list(folders)
        self.context = context or _Context()
        self.ensured: list[str] = []
        self.uploaded: tuple[str, bytes] | None = None

    def get_files(self, recursive: bool = False) -> _Collection:
        assert recursive
        return _Collection(self._files)

    def get_folders(self, recursive: bool = False) -> _Collection:
        assert recursive
        return _Collection(self._folders)

    def ensure_folders(self, paths) -> list:
        self.ensured.extend(paths)
        return []

    def upload_file(self, path: str, content: bytes) -> _Request:
        self.uploaded = (path, content)
        return _Request(path, True)


def _folder_item(dest_path: str) -> MigrationItem:
    return MigrationItem(source_path=f"/sites/src/{dest_path}", dest_path=dest_path, item_type="folder")


def test_library_target_list_paths_skips_system_scaffolding():
    folder = _TargetFolder(
        files=[
            _Entry("/sites/x/Docs/report.docx"),
            _Entry("/sites/x/Docs/sub/data.csv"),
            _Entry("/sites/x/Docs/Forms/AllItems.aspx"),
            _Entry("/sites/x/Docs/desktop.ini"),
        ],
        folders=[
            _Entry("/sites/x/Docs/Archive"),
            _Entry("/sites/x/Docs/sub"),
            _Entry("/sites/x/Docs/Forms"),
        ],
    )
    target = SharePointLibraryTarget(folder)

    assert target.list_paths() == ["report.docx", "sub/data.csv", "Archive/", "sub/"]


def test_library_target_list_paths_relative_to_subfolder():
    folder = _TargetFolder(
        files=[
            _Entry("/sites/x/Docs/archive/old.txt"),
            _Entry("/sites/x/Docs/archive/Forms/AllItems.aspx"),
        ],
        folders=[_Entry("/sites/x/Docs/archive/nested"), _Entry("/sites/x/Docs/archive/Forms")],
    )
    folder.server_relative_url = "/sites/x/Docs/archive"
    target = SharePointLibraryTarget(folder)

    assert target.list_paths() == ["old.txt", "nested/"]


def test_library_target_write_ensures_folders_instead_of_uploading():
    folder = _TargetFolder()
    target = SharePointLibraryTarget(folder)

    target.write(_folder_item("a/b/"), None)

    assert folder.ensured == ["a/b"]
    assert folder.uploaded is None
    assert folder.context.executed == 1


def test_library_target_write_uploads_files():
    folder = _TargetFolder()
    target = SharePointLibraryTarget(folder)

    target.write(MigrationItem("/sites/src/a.txt", "a.txt"), b"data")

    assert folder.uploaded == ("a.txt", b"data")
    assert folder.ensured == []


def test_library_target_write_many_creates_folders_and_transfers_files(monkeypatch):
    folder = _TargetFolder()
    target = SharePointLibraryTarget(folder)
    captured: dict = {}

    def _fake_transfer(target_folder, files, *, concurrency=4, **kwargs):
        captured["files"] = list(files)
        return []

    monkeypatch.setattr(
        "office365.migration.sharepoint.transfer._transfer_files_parallel",
        _fake_transfer,
    )

    failures = target.write_many(
        [_folder_item("empty/"), MigrationItem("/sites/src/a.txt", "a.txt")],
        [None, b"data"],
    )

    assert failures == []
    assert folder.ensured == ["empty"]
    assert captured["files"] == [("a.txt", b"data")]


def test_library_target_exists_distinguishes_folders_and_files():
    web = _Web(folders={"/sites/x/Docs/a"}, files={"/sites/x/Docs/a/f.txt"})
    folder = _TargetFolder(context=_Context(web))
    target = SharePointLibraryTarget(folder)

    assert target.exists(_folder_item("a/")) is True
    assert target.exists(_folder_item("b/")) is False
    assert target.exists(MigrationItem("/sites/src/a/f.txt", "a/f.txt")) is True
    assert target.exists(MigrationItem("/sites/src/a/g.txt", "a/g.txt")) is False


def test_library_target_folder_checksum_is_empty_hash():
    target = SharePointLibraryTarget(_TargetFolder())

    assert target.checksum(_folder_item("a/")) == target.checksum(_folder_item("b/"))


def test_library_target_read_folder_returns_empty_bytes():
    target = SharePointLibraryTarget(_TargetFolder())

    assert target.read(_folder_item("a/")) == b""


class _AuthorListItem:
    def __init__(self, author_id: int, editor_id: int) -> None:
        self._author_id = author_id
        self._editor_id = editor_id
        self.properties: dict = {}
        self.reads = 0

    def get(self) -> "_AuthorListItem":
        return self

    def execute_query(self) -> "_AuthorListItem":
        self.reads += 1
        self.properties = {"AuthorId": self._author_id, "EditorId": self._editor_id}
        return self


class _AuthorSecurableFile:
    def __init__(self, author_id: int, editor_id: int) -> None:
        self.listItemAllFields = _AuthorListItem(author_id, editor_id)


class _AuthorUser:
    def __init__(self, login_name: str) -> None:
        self.login_name = login_name


class _AuthorUserQuery:
    def __init__(self, user: _AuthorUser) -> None:
        self._user = user

    def get(self) -> "_AuthorUserQuery":
        return self

    def execute_query(self) -> _AuthorUser:
        return self._user


class _AuthorSiteUsers:
    def __init__(self, users: dict[int, str]) -> None:
        self._users = users

    def get_by_id(self, uid: int) -> _AuthorUserQuery:
        return _AuthorUserQuery(_AuthorUser(self._users[uid]))


class _AuthorshipWeb:
    def __init__(self, users: dict[int, str]) -> None:
        self.site_users = _AuthorSiteUsers(users)
        self.files: dict[str, _AuthorSecurableFile] = {}

    def get_file_by_server_relative_url(self, url: str) -> _AuthorSecurableFile:
        return self.files.setdefault(url, _AuthorSecurableFile(12, 7))


def test_library_target_read_authorship_re_reads_written_item():
    """A stale ``listItemAllFields`` has no AuthorId/EditorId; the read must refresh."""
    web = _AuthorshipWeb({12: "vgrem@x", 7: "mdoe@x"})
    target = SharePointLibraryTarget(_TargetFolder(context=_Context(web=web)))
    item = MigrationItem("/sites/src/doc.txt", "doc.txt", item_type="file")

    assert target.read_authorship(item) == ("vgrem@x", "mdoe@x")
    assert web.files["/sites/x/Docs/doc.txt"].listItemAllFields.reads == 1


def test_library_target_list_paths_skips_site_assets_scaffolding():
    web = _SiteAssetsWeb("Project")
    folder = _TargetFolder(
        files=[
            _Entry("/sites/x/SiteAssets/__siteIcon__.png"),
            _Entry("/sites/x/SiteAssets/logo.png"),
        ],
        folders=[
            _Entry("/sites/x/SiteAssets/Project Notebook"),
            _Entry("/sites/x/SiteAssets/Images"),
            _Entry("/sites/x/SiteAssets/Forms"),
        ],
        context=_Context(web),
    )
    folder.server_relative_url = "/sites/x/SiteAssets"
    target = SharePointLibraryTarget(folder)

    assert target.list_paths() == ["logo.png", "Images/"]


def test_site_assets_notebook_rule_does_not_apply_elsewhere():
    folder = _TargetFolder(folders=[_Entry("/sites/x/Docs/Project Notebook")])
    target = SharePointLibraryTarget(folder)

    assert target.list_paths() == ["Project Notebook/"]


class _ById:
    id = None


class _SourceFile:
    def __init__(self, url: str) -> None:
        self.server_relative_url = url
        self.length = 1
        self.author = _ById()
        self.modified_by = _ById()
        self.time_last_modified = None
        self.time_created = None
        self.unique_id = None
        self.ui_version_label = None


class _SourceFolder:
    def __init__(self, url: str, web, files=(), folders=()) -> None:
        self.server_relative_url = url
        self.context = _Context(web)
        self._files = list(files)
        self._folders = list(folders)

    def get_files(self, recursive: bool = False) -> _Collection:
        return _Collection(self._files)

    def get_folders(self, recursive: bool = False) -> _Collection:
        return _Collection(self._folders)


def test_library_source_skips_site_assets_scaffolding():
    web = _SiteAssetsWeb("Project")
    folder = _SourceFolder(
        "/sites/x/SiteAssets",
        web,
        files=[
            _SourceFile("/sites/x/SiteAssets/__siteIcon__.png"),
            _SourceFile("/sites/x/SiteAssets/logo.png"),
        ],
        folders=[
            _Entry("/sites/x/SiteAssets/Project Notebook"),
            _Entry("/sites/x/SiteAssets/Images"),
            _Entry("/sites/x/SiteAssets/Forms"),
        ],
    )
    source = SharePointLibrarySource(folder)
    source._item_authors = {}

    assert [item.dest_path for item in source.list_items()] == ["Images/", "logo.png"]


# ── Document timestamps (web-local conversion) ────────────────────────────────


class _Conversion:
    def __init__(self, value: datetime, offset_hours: int) -> None:
        self._value = value
        self._offset = offset_hours
        self.value = None


class _FakeTimeZone:
    def __init__(self, offset_hours: int) -> None:
        self.offset_hours = offset_hours
        self.pending: list[_Conversion] = []
        self.calls: list[str] = []

    def utc_to_local_time(self, value: datetime) -> _Conversion:
        self.calls.append(value)
        conversion = _Conversion(value, self.offset_hours)
        self.pending.append(conversion)
        return conversion


class _RegionalSettings:
    def __init__(self, time_zone: _FakeTimeZone) -> None:
        self.time_zone = time_zone


class _FakeUpdateValue:
    def __init__(self) -> None:
        self.updates: list[tuple[dict, bool | None, bool]] = []

    def validate_update_list_item(
        self, form_values, new_document_update=False, checkin_comment=None, dates_in_utc=None
    ) -> "_Executable":
        self.updates.append((dict(form_values), dates_in_utc, new_document_update))
        return _Executable()


class _Executable:
    def execute_query(self) -> "_Executable":
        return self


class _SecurableFile:
    def __init__(self) -> None:
        self.listItemAllFields = _FakeUpdateValue()


class _TimestampContext:
    def __init__(self, web) -> None:
        self.web = web
        self.executed = 0

    def execute_query(self) -> None:
        self.executed += 1
        time_zone = self.web.regional_settings.time_zone
        for conversion in list(time_zone.pending):
            conversion.value = conversion._value + timedelta(hours=time_zone.offset_hours)
        time_zone.pending = []


class _TimestampFolder:
    server_relative_url = "/sites/x/Docs"

    def __init__(self, context: _TimestampContext) -> None:
        self.context = context


class _TimestampWeb:
    def __init__(self, time_zone: _FakeTimeZone) -> None:
        self.regional_settings = _RegionalSettings(time_zone)
        self._files: dict[str, _SecurableFile] = {}

    def get_file_by_server_relative_url(self, url: str) -> _SecurableFile:
        return self._files.setdefault(url, _SecurableFile())


def test_library_target_converts_utc_to_web_local_before_writing_timestamps():
    time_zone = _FakeTimeZone(offset_hours=-7)  # Pacific daylight
    web = _TimestampWeb(time_zone)
    folder = _TimestampFolder(_TimestampContext(web))
    target = SharePointLibraryTarget(folder)
    item = MigrationItem(
        "/sites/src/doc.txt",
        "doc.txt",
        item_type="file",
        created="2021-06-01T15:00:00+00:00",
        modified="2022-07-02T16:00:00+00:00",
    )

    target.apply_timestamps(item)

    file = web._files["/sites/x/Docs/doc.txt"]
    form_values, dates_in_utc, new_document_update = file.listItemAllFields.updates[0]
    # 15:00Z -> 08:00 local; 16:00Z -> 09:00 local
    assert form_values == {"Created": "2021-06-01 08:00:00", "Modified": "2022-07-02 09:00:00"}
    assert dates_in_utc is True
    assert new_document_update is True


def test_library_target_caches_time_zone_conversions():
    time_zone = _FakeTimeZone(offset_hours=0)
    web = _TimestampWeb(time_zone)
    target = SharePointLibraryTarget(_TimestampFolder(_TimestampContext(web)))
    item = MigrationItem(
        "/sites/src/doc.txt",
        "doc.txt",
        item_type="file",
        created="2021-06-01T15:00:00+00:00",
        modified="2021-06-01T15:00:00+00:00",
    )

    target.apply_timestamps(item)
    target.apply_timestamps(item)

    assert len(time_zone.calls) == 1  # converted once, then cached
    assert time_zone.calls[0].replace(tzinfo=None) == datetime(2021, 6, 1, 15, 0, 0)
