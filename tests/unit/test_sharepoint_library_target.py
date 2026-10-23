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

from datetime import datetime, timedelta, timezone

from office365.migration.base import MigrationItem, Principal
from office365.migration.sharepoint.adapters import SharePointLibrarySource, SharePointLibraryTarget


class _Entry:
    def __init__(self, server_relative_url: str) -> None:
        self.server_relative_url = server_relative_url
        self.time_created = None
        self.time_last_modified = None


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


def test_library_target_write_uploads_files():
    folder = _TargetFolder()
    target = SharePointLibraryTarget(folder)

    target.write(MigrationItem("/sites/src/a.txt", "a.txt"), b"data")

    assert folder.uploaded == ("a.txt", b"data")
    assert folder.ensured == []


def test_library_target_folder_checksum_is_empty_hash():
    target = SharePointLibraryTarget(_TargetFolder())

    assert target.checksum(_folder_item("a/")) == target.checksum(_folder_item("b/"))


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


class _ById:
    id = None


class _SourceFile:
    def __init__(self, url: str, minor_version: int = 0) -> None:
        self.server_relative_url = url
        self.length = 1
        self.author = _ById()
        self.modified_by = _ById()
        self.time_last_modified = None
        self.time_created = None
        self.unique_id = None
        self.ui_version_label = None
        self.minor_version = minor_version


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


class _TargetUser:
    def __init__(self, user_id: int, login_name: str) -> None:
        self.id = user_id
        self.login_name = login_name


class _EnsureUser:
    def __init__(self, user: _TargetUser) -> None:
        self._user = user

    def execute_query(self) -> _TargetUser:
        return self._user


class _TimestampWeb:
    def __init__(self, time_zone: _FakeTimeZone) -> None:
        self.regional_settings = _RegionalSettings(time_zone)
        self._files: dict[str, _SecurableFile] = {}

    def ensure_user(self, login: str) -> _EnsureUser:
        return _EnsureUser(_TargetUser(9, login))

    def get_file_by_server_relative_url(self, url: str) -> _SecurableFile:
        return self._files.setdefault(url, _SecurableFile())


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


def test_library_target_folds_authorship_into_the_timestamp_write():
    web = _TimestampWeb(_FakeTimeZone(offset_hours=0))
    target = SharePointLibraryTarget(_TimestampFolder(_TimestampContext(web)))
    item = MigrationItem(
        "/sites/src/doc.txt",
        "doc.txt",
        item_type="file",
        created="2021-06-01T15:00:00+00:00",
        modified="2022-07-02T16:00:00+00:00",
    )
    item.author = Principal("i:0#.f|membership|vgrem@x.onmicrosoft.com", "1", "Vadim")

    target.apply_authorship(item)
    target.apply_timestamps(item)

    updates = web._files["/sites/x/Docs/doc.txt"].listItemAllFields.updates
    assert len(updates) == 1  # authorship did not pay a write of its own
    form_values, _, _ = updates[0]
    assert form_values["Created"] == "2021-06-01 15:00:00"
    assert form_values["Author"].LookupId == 9  # noqa: PLR2004


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
    """A deferred ``Folder``: its list item carries the column values, the folder
    resource reports the system metadata that the timestamp write lands on."""

    def __init__(self, item: _FolderItem) -> None:
        self.list_item_all_fields = item
        self.time_created = None
        self.time_last_modified = None
        self.reads = 0

    def get(self) -> "_FolderHandle":
        self.reads += 1
        return self

    def execute_query(self) -> "_FolderHandle":
        return self


class _FolderWeb:
    def __init__(self, items: dict[str, _FolderItem]) -> None:
        self._items = items
        self._handles: dict[str, _FolderHandle] = {}

    def get_folder_by_server_relative_path(self, url: str) -> _FolderHandle:
        if url not in self._handles:
            self._handles[url] = _FolderHandle(self._items.setdefault(url, _FolderItem()))
        return self._handles[url]

    def handle(self, url: str) -> _FolderHandle:
        return self.get_folder_by_server_relative_path(url)


def _folder_target(web: _FolderWeb, columns: list[_Column] | None = None) -> SharePointLibraryTarget:
    folder = _TargetFolder(context=_Context(web=web))
    return SharePointLibraryTarget(folder, sp_list=_Library(columns or [_Column("Region", "Choice")]))


def test_library_target_reports_folder_values_it_could_not_write():
    item = _FolderItem(error="Access denied")
    target = _folder_target(_FolderWeb({"/sites/x/Docs/Area1": item}))

    target.write(_folder_item("Area1/"), {"Region": "North"})

    assert any("folder column values for 'Area1/'" in warning for warning in target.warnings)


def test_library_target_reads_a_folders_metadata_back_from_the_folder_resource():
    # The folder's list item is where the timestamp write lands; the folder resource
    # reports the same instant, and it is what the source side reads too.
    web = _FolderWeb({"/sites/x/Docs/Area1": _FolderItem({"Region": "North"})})
    handle = web.handle("/sites/x/Docs/Area1")
    handle.time_created = datetime(2021, 3, 4, 5, 6, 7, tzinfo=timezone.utc)
    handle.time_last_modified = datetime(2021, 3, 5, 6, 7, 8, tzinfo=timezone.utc)

    metadata = _folder_target(web).read_metadata(_folder_item("Area1/"))

    assert metadata == {"created": "2021-03-04T05:06:07+00:00", "modified": "2021-03-05T06:07:08+00:00"}
    assert handle.reads == 1


# ── Content-approval (moderation) state ───────────────────────────────────────


class _ModerationItem:
    def __init__(self, properties: dict) -> None:
        self.properties = properties


class _ModerationItems:
    """The library's items collection, which records the projection it was given."""

    def __init__(self, items: list[_ModerationItem]) -> None:
        self._items = items
        self.selects: list[list[str]] = []
        self.expands: list[list[str]] = []

    def select(self, columns) -> "_ModerationItems":
        self.selects.append(list(columns))
        return self

    def expand(self, names) -> "_ModerationItems":
        self.expands.append(list(names))
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


# ── Checked-out files (in-progress edits REST cannot see) ────────────────────


# ── Un-published (minor) versions (the draft hides its published predecessor) ──


# ── Folder system metadata (a folder is an item too) ─────────────────────────


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
