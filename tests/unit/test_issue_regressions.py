"""Offline regression tests for previously fixed issues.

- #884: apostrophes in File.open_binary/save_binary paths
- #793: upload size from in-memory (io.BytesIO) streams
- #875: sharing-token encoding (UTF-8, padding stripped)
- #881: DriveItem.download_folder paginates children (no 200-item cap)
- #978: File.open_binary/save_binary keep the OData call syntax literal
"""

from __future__ import annotations

import base64
import io
import os
import tempfile
import unittest

import pytest
from office365.graph_client import GraphClient
from office365.onedrive.internal.paths.shared import _url_to_shared_token
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.collection import _stream_size
from office365.sharepoint.files.file import File
from requests import Response
from tests import test_site_url


class _CaptureTransport(BaseTransport):
    def __init__(self):
        super().__init__()
        self.url = ""

    def execute(self, request):
        self.url = request.url
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        resp.headers["Content-Type"] = "application/octet-stream"
        resp._content = b"payload"
        return resp


class TestFilePathQuoting(unittest.TestCase):
    """Apostrophes in server-relative paths must be escaped in the DecodedUrl literal."""

    def _context(self) -> tuple[ClientContext, _CaptureTransport]:
        ctx = ClientContext(test_site_url)
        transport = _CaptureTransport()
        ctx.pending_request().beforeExecute.clear()
        ctx.pending_request().transport = transport
        return ctx, transport

    def test_read_escapes_apostrophe(self):
        ctx, transport = self._context()
        result = File.open_binary(ctx, "/sites/x/Shared Documents/macdonald's file.txt")

        self.assertEqual(result.content, b"payload")
        self.assertIn("getFileByServerRelativePath", transport.url)
        self.assertIn("macdonald%27%27s", transport.url)

    def test_odata_call_syntax_stays_literal(self):
        """#978: only the path value is encoded — the call, parens and $value stay literal."""
        ctx, transport = self._context()
        File.open_binary(ctx, "/sites/x/Shared Documents/Folder 1/conversation.docx")

        self.assertIn("getFileByServerRelativePath(DecodedUrl='", transport.url)
        self.assertTrue(transport.url.endswith(")/$value"))
        self.assertIn("Folder%201", transport.url)  # the value itself is encoded
        for encoded in ("%28", "%29", "%24", "%5C"):
            self.assertNotIn(encoded, transport.url)

    def test_write_odata_call_syntax_stays_literal(self):
        ctx, transport = self._context()
        File.save_binary(ctx, "/sites/x/Shared Documents/Folder 1/conversation.docx", b"content")

        self.assertIn("getFileByServerRelativePath(DecodedUrl='", transport.url)
        self.assertTrue(transport.url.endswith(")/$value"))
        self.assertNotIn("%5C", transport.url)


class _Unseekable(io.BytesIO):
    def seek(self, *args, **kwargs):
        raise io.UnsupportedOperation("seek")


def test_stream_size_from_bytesio():
    data = b"x" * 12345
    stream = io.BytesIO(data)
    assert _stream_size(stream) == len(data)
    assert stream.tell() == 0  # position preserved


def test_stream_size_from_bytesio_mid_stream():
    stream = io.BytesIO(b"abcdef")
    offset = 2
    stream.seek(offset)
    assert _stream_size(stream) == 6  # noqa: PLR2004
    assert stream.tell() == offset  # position preserved


def test_stream_size_from_real_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"y" * 777)
        path = f.name
    try:
        with open(path, "rb") as f:
            assert _stream_size(f) == 777  # noqa: PLR2004
    finally:
        os.unlink(path)


def test_stream_size_rejects_unseekable_source():
    with pytest.raises(ValueError, match="seekable"):
        _stream_size(_Unseekable(b"data"))


def _reference(url: str) -> str:
    b64 = base64.b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
    return "u!" + b64.replace("/", "_").replace("+", "-")


def test_all_base64_padding_is_removed():
    # a url whose base64 ends with '==' must leave no '=' in the token
    url = "https://a"
    token = _url_to_shared_token(url)
    assert token.startswith("u!")
    assert "=" not in token
    assert token == _reference(url)


class _FolderChild:
    def __init__(self, name: str, is_file: bool = True):
        self.name = name
        self.is_file = is_file
        self.downloaded = False

    def get_content(self):
        child = self

        class _Result:
            def after_execute(self_inner, _action):
                child.downloaded = True
                return self_inner

        return _Result()


def test_download_folder_paginates_children():
    """#881: every child is queued for download, not just the first Graph page."""
    client = GraphClient()
    folder = client.me.drive.root
    pages = [[_FolderChild("a.txt")], [_FolderChild("b.txt")]]

    class _Children(list):
        def get_all(self, page_size=None, page_loaded=None, progress=None):
            accumulated: list = []
            for page in pages:
                accumulated = accumulated + page
                page_loaded(accumulated)
            return self

    folder._properties["children"] = _Children()
    folder.download_folder(io.BytesIO(), recursive=False)

    assert all(child.downloaded for page in pages for child in page)
