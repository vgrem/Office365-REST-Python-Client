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


# ── Folder column values (a folder is a list item too) ────────────────────────


class _Column:
    """A library column as returned by a ``fields`` projection."""

    def __init__(self, internal_name: str, type_as_string: str = "Text", *, hidden=False, read_only=False) -> None:
        self.properties = {
            "InternalName": internal_name,
            "TypeAsString": type_as_string,
            "Hidden": hidden,
            "ReadOnlyField": read_only,
        }
        self.id = None
        self.schema_xml = None

    @property
    def internal_name(self) -> str:
        return self.properties["InternalName"]

    @property
    def type_as_string(self) -> str:
        return self.properties["TypeAsString"]

    @property
    def hidden(self) -> bool:
        return self.properties["Hidden"]

    @property
    def read_only_field(self) -> bool:
        return self.properties["ReadOnlyField"]


class _Fields:
    def __init__(self, columns: list[_Column]) -> None:
        self._columns = columns

    def select(self, _columns) -> "_Fields":
        return self

    def get(self) -> "_Fields":
        return self

    def execute_query(self) -> list[_Column]:
        return self._columns


class _Library:
    def __init__(self, columns: list[_Column]) -> None:
        self.fields = _Fields(columns)


class _FolderItem:
    """A folder's underlying list item (MERGE target and read-back source)."""

    def __init__(self, properties: dict | None = None, error: str | None = None) -> None:
        self.properties = dict(properties or {})
        self.written: dict = {}
        self.updated = 0
        self._error = error

    def select(self, columns) -> "_FolderItem":
        self._select = list(columns)
        return self

    def get(self) -> "_FolderItem":
        return self

    def set_property(self, name: str, value) -> "_FolderItem":
        self.written[name] = value
        return self

    def update(self) -> "_FolderItem":
        if self._error is not None:
            raise ValueError(self._error)
        self.updated += 1
        return self

    def execute_query(self) -> "_FolderItem":
        return self


class _FolderHandle:
    def __init__(self, item: _FolderItem) -> None:
        self.list_item_all_fields = item


class _FolderWeb:
    def __init__(self, items: dict[str, _FolderItem]) -> None:
        self._items = items

    def get_folder_by_server_relative_path(self, url: str) -> _FolderHandle:
        return _FolderHandle(self._items.setdefault(url, _FolderItem()))


def _folder_target(web: _FolderWeb, columns: list[_Column] | None = None) -> SharePointLibraryTarget:
    folder = _TargetFolder(context=_Context(web=web))
    return SharePointLibraryTarget(folder, sp_list=_Library(columns or [_Column("Region", "Choice")]))


def test_library_target_applies_folder_column_values_to_its_item():
    item = _FolderItem()
    web = _FolderWeb({"/sites/x/Docs/Area1": item})
    target = _folder_target(web)

    target.write(
        _folder_item("Area1/"),
        # ``FileRef``/``FSObjType`` are the folder's identity, and an empty value is
        # no value — none of them can be written.
        {"Region": "North", "ContentTypeId": "0x0120", "FileRef": "/sites/x/Docs/Area1", "Title": ""},
    )

    assert item.written == {"Region": "North", "ContentTypeId": "0x0120"}
    assert item.updated == 1


def test_library_target_reports_folder_values_it_could_not_write():
    item = _FolderItem(error="Access denied")
    target = _folder_target(_FolderWeb({"/sites/x/Docs/Area1": item}))

    target.write(_folder_item("Area1/"), {"Region": "North"})

    assert any("folder column values for 'Area1/'" in warning for warning in target.warnings)


def test_library_target_folder_checksum_compares_read_back_values():
    matching = _folder_target(_FolderWeb({"/sites/x/Docs/Area1": _FolderItem({"Region": "North"})}))
    differing = _folder_target(_FolderWeb({"/sites/x/Docs/Area1": _FolderItem({"Region": "South"})}))
    same_folder_elsewhere = _folder_target(_FolderWeb({"/sites/x/Docs/Area2": _FolderItem({"Region": "North"})}))

    assert matching.checksum(_folder_item("Area1/"))  # a real hash, so the check can run
    assert matching.checksum(_folder_item("Area1/")) == same_folder_elsewhere.checksum(_folder_item("Area2/"))
    assert differing.checksum(_folder_item("Area1/")) != matching.checksum(_folder_item("Area1/"))


def test_library_target_without_the_library_cannot_compare_folder_values():
    plain = SharePointLibraryTarget(_TargetFolder())

    assert plain.supports_folder_records is False
    assert plain.checksum(_folder_item("Area1/")) == ""
    assert _folder_target(_FolderWeb({})).supports_folder_records is True


def test_library_source_without_the_library_reports_no_folder_records():
    folder = _SourceFolder("/sites/x/Docs", _Web())

    assert SharePointLibrarySource(folder).supports_folder_records is False


# ── Content-approval (moderation) state ───────────────────────────────────────


class _ModerationItem:
    def __init__(self, properties: dict) -> None:
        self.properties = properties


class _ModerationItems:
    """The library's items collection, which records the projection it was given."""

    def __init__(self, items: list[_ModerationItem]) -> None:
        self._items = items
        self.selects: list[list[str]] = []

    def select(self, columns) -> "_ModerationItems":
        self.selects.append(list(columns))
        return self

    def get_all(self) -> "_ModerationItems":
        return self

    def execute_query(self) -> "_ModerationItems":
        return self

    def __iter__(self):
        return iter(self._items)


class _ModerationList:
    def __init__(self, items: list[_ModerationItem], moderation: bool = True) -> None:
        self.items = _ModerationItems(items)
        self.properties = {"EnableModeration": moderation}
        self.ensured: list[list[str]] = []

    def ensure_properties(self, names) -> "_ModerationList":
        self.ensured.append(list(names))
        return self

    def get(self) -> "_ModerationList":
        return self

    def execute_query(self) -> "_ModerationList":
        return self


def _library_source(state: dict | None, moderation: bool = True):
    """A source over one file, whose list reports the given approval columns."""
    url = "/sites/x/Docs/doc.txt"
    folder = _SourceFolder("/sites/x/Docs", _Web(), files=[_SourceFile(url)])
    properties = {"FileRef": url}
    properties.update(state or {})
    lst = _ModerationList([_ModerationItem(properties)], moderation=moderation)
    return SharePointLibrarySource(folder, sp_list=lst), lst


def test_library_source_reads_a_draft_files_approval_state():
    # An uploaded file starts out approved, so only a draft/pending or rejected
    # source file needs its state carried — with its approval comments.
    source, _ = _library_source({"OData__ModerationStatus": 0, "OData__ModerationComments": "wip"})
    item = source.list_items()[0]

    assert source.read_item_state(item) == {"_ModerationStatus": "0", "_ModerationComments": "wip"}
    # the same read feeds the verification diff, which needs the status even when
    # nothing had to be written
    assert source.read_metadata(item)["moderation_status"] == "0"


def test_library_source_does_not_carry_an_approved_files_state():
    source, _ = _library_source({"OData__ModerationStatus": 2})
    item = source.list_items()[0]

    assert source.read_item_state(item) is None
    assert source.read_metadata(item)["moderation_status"] == "2"


def test_library_source_does_not_read_moderation_columns_without_moderation():
    # Selecting a column the list does not have fails outright, so the projection
    # only grows when the library enables content approval.
    source, lst = _library_source({}, moderation=False)
    item = source.list_items()[0]

    assert source.read_item_state(item) is None
    assert "moderation_status" not in source.read_metadata(item)
    assert "OData__ModerationStatus" not in lst.items.selects[-1]
    assert lst.ensured == [["EnableModeration"]]


def test_library_source_without_the_library_cannot_read_approval_state():
    source = SharePointLibrarySource(_SourceFolder("/sites/x/Docs", _Web()))

    assert source.supports_item_state is False
    assert source.read_item_state(MigrationItem("/sites/x/Docs/doc.txt", "doc.txt")) is None


def _state_target():
    web = _TimestampWeb(_FakeTimeZone(offset_hours=-7))
    return SharePointLibraryTarget(_TimestampFolder(_TimestampContext(web))), web


def test_library_target_restores_a_files_approval_state_in_its_own_write():
    # A moderated document rejects a moderation change combined with other item
    # properties, so this is a write of its own, sent after the timestamps.
    target, web = _state_target()
    item = MigrationItem("/sites/x/Docs/doc.txt", "doc.txt")

    target.apply_item_state(item, {"_ModerationStatus": "0", "_ModerationComments": "wip"})

    file = web.get_file_by_server_relative_url("/sites/x/Docs/doc.txt")
    assert file.listItemAllFields.updates == [({"_ModerationStatus": "0", "_ModerationComments": "wip"}, True, True)]


def test_library_target_skips_approval_state_for_folders():
    target, web = _state_target()
    item = MigrationItem("/sites/x/Docs/Area1", "Area1/", item_type="folder")

    target.apply_item_state(item, {"_ModerationStatus": "0"})

    assert web._files == {}


def test_library_target_reports_an_approval_state_it_could_not_restore():
    target, web = _state_target()
    file = web.get_file_by_server_relative_url("/sites/x/Docs/doc.txt")

    class _Rejected:
        def validate_update_list_item(self, form_values, **_kwargs):
            raise ValueError("You cannot change moderation status and set other item properties")

    file.listItemAllFields = _Rejected()

    target.apply_item_state(MigrationItem("/sites/x/Docs/doc.txt", "doc.txt"), {"_ModerationStatus": "0"})

    assert any("approval state for 'doc.txt'" in warning for warning in target.warnings)


class _MetaListItem:
    """The file's list item: the only place its approval status is exposed."""

    def __init__(self, status, fails: bool = False) -> None:
        self._status = status
        self._fails = fails
        self.selected: list[str] = []
        self.properties: dict = {}

    def select(self, columns) -> "_MetaListItem":
        self.selected = list(columns)
        return self

    def get(self) -> "_MetaListItem":
        return self

    def execute_query(self) -> "_MetaListItem":
        if self._fails:
            raise ValueError("Column 'OData__ModerationStatus' does not exist")
        self.properties = {"OData__ModerationStatus": self._status}
        return self


class _MetaFile:
    def __init__(self, item: _MetaListItem) -> None:
        self.time_created = None
        self.time_last_modified = None
        self.length = 3
        self.listItemAllFields = item

    def get(self) -> "_MetaFile":
        return self

    def execute_query(self) -> "_MetaFile":
        return self


class _MetaWeb:
    def __init__(self, item: _MetaListItem) -> None:
        self._item = item

    def get_file_by_server_relative_url(self, _url: str) -> _MetaFile:
        return _MetaFile(self._item)


def _meta_target(item: _MetaListItem) -> SharePointLibraryTarget:
    return SharePointLibraryTarget(_TargetFolder(context=_Context(web=_MetaWeb(item))))


def test_library_target_reads_back_the_written_approval_state():
    target = _meta_target(_MetaListItem(1))

    metadata = target.read_metadata(MigrationItem("/sites/x/Docs/doc.txt", "doc.txt"))

    assert metadata["moderation_status"] == "1"


def test_library_target_omits_the_approval_state_it_cannot_read():
    # A library without moderation enabled has no such column: the difference is
    # unknown, not a mismatch.
    target = _meta_target(_MetaListItem(None, fails=True))

    metadata = target.read_metadata(MigrationItem("/sites/x/Docs/doc.txt", "doc.txt"))

    assert "moderation_status" not in metadata
