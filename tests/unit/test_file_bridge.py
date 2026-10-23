"""Unit tests for the DataFrame <-> SharePoint file bridge.

- ``Folder.write_dataframe`` serializes a DataFrame and writes it as a file.
- ``File.write_dataframe`` serializes a DataFrame into a file's content.
- ``List.from_file`` downloads a SharePoint-hosted file and streams it.
- ``dataframe_to_bytes``/``dataframe_from_bytes`` are the content codecs.
"""

from __future__ import annotations

import io

import pytest
from office365.runtime.converters.dataframe import dataframe_from_bytes, dataframe_to_bytes
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.lists.list import List

pd = pytest.importorskip("pandas")


class _CaptureFolder(Folder):
    def __init__(self) -> None:
        self.captured = None

    def upload_file(self, relative_path, content, chunk_size=None, progress=None):
        self.captured = (relative_path, content)


def test_write_dataframe_csv_writes_utf8_sig_bytes():
    folder = _CaptureFolder()

    folder.write_dataframe("data.csv", pd.DataFrame({"a": [1, 2]}))

    path, content = folder.captured
    assert path == "data.csv"
    assert isinstance(content, bytes)
    assert content.startswith(b"\xef\xbb\xbf")  # utf-8-sig BOM for Excel
    assert b"a" in content and b"1" in content


def test_dataframe_bytes_round_trip_csv():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})

    back = dataframe_from_bytes(dataframe_to_bytes(df))

    assert list(back["a"]) == [1, 2]
    assert list(back["b"]) == ["x", "y"]


class _FakeFile:
    def __init__(self, content: bytes) -> None:
        self._content = content

    def read(self) -> bytes:
        return self._content


class _FakeWeb:
    def __init__(self, content: bytes) -> None:
        self._content = content
        self.url = None

    def get_file_by_server_relative_url(self, url: str) -> _FakeFile:
        self.url = url
        return _FakeFile(self._content)


class _FakeContext:
    def __init__(self, content: bytes) -> None:
        self.web = _FakeWeb(content)


class _CaptureList(List):
    def __init__(self, content: bytes) -> None:
        self._context = _FakeContext(content)
        self.import_args = None

    def from_records(self, source, **opts):
        self.import_args = (source, opts)
        return "driver"


def test_from_file_downloads_and_streams_csv():
    csv = b"Name,date\nAAPL,2020-01-01\n"
    lst = _CaptureList(csv)

    result = lst.from_file("Shared Documents/stocks.csv", key=["Name", "date"])

    assert result == "driver"
    assert lst.context.web.url == "Shared Documents/stocks.csv"
    source, opts = lst.import_args
    assert isinstance(source, io.BytesIO)
    assert source.getvalue() == csv
    assert opts["format"] == "csv"
    assert opts["key"] == ["Name", "date"]


def test_from_file_reads_xlsx_into_dataframe():
    pytest.importorskip("openpyxl")
    buffer = io.BytesIO()
    pd.DataFrame({"a": [1]}).to_excel(buffer, index=False)
    lst = _CaptureList(buffer.getvalue())

    lst.from_file("Shared Documents/stocks.xlsx", format="xlsx")

    source, opts = lst.import_args
    assert isinstance(source, pd.DataFrame)
    assert opts["format"] == "dataframe"
