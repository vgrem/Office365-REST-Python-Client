"""Offline tests for the document-library target adapter.

Covers the verification enumeration: a target library always contains
SharePoint-owned scaffolding (``Forms/``, ``desktop.ini``) that the source
projection deliberately skips, so the target must skip it too or every migrated
library is reported as having "extra" content.
"""

from __future__ import annotations

from office365.migration.sharepoint.adapters import SharePointLibraryTarget


class _File:
    def __init__(self, server_relative_url: str) -> None:
        self.server_relative_url = server_relative_url


class _Files:
    def __init__(self, files: list[_File]) -> None:
        self._files = files

    def execute_query(self) -> list[_File]:
        return self._files


class _TargetFolder:
    server_relative_url = "/sites/x/Docs"

    def __init__(self, files: list[_File]) -> None:
        self._files = files

    def get_files(self, recursive: bool = False) -> _Files:
        assert recursive
        return _Files(self._files)


def test_library_target_list_paths_skips_system_scaffolding():
    folder = _TargetFolder(
        [
            _File("/sites/x/Docs/report.docx"),
            _File("/sites/x/Docs/sub/data.csv"),
            _File("/sites/x/Docs/Forms/AllItems.aspx"),
            _File("/sites/x/Docs/desktop.ini"),
        ]
    )
    target = SharePointLibraryTarget(folder)

    assert target.list_paths() == ["report.docx", "sub/data.csv"]


def test_library_target_list_paths_relative_to_subfolder():
    folder = _TargetFolder(
        [
            _File("/sites/x/Docs/archive/old.txt"),
            _File("/sites/x/Docs/archive/Forms/AllItems.aspx"),
        ]
    )
    folder.server_relative_url = "/sites/x/Docs/archive"
    target = SharePointLibraryTarget(folder)

    assert target.list_paths() == ["old.txt"]
