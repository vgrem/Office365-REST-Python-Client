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
