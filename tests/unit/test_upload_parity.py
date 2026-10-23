"""Offline tests for the SharePoint upload-parity helpers.

``FileCollection.upload_file`` uploads a local path or binary stream, dispatching
by size (simple request vs resumable session); ``Folder.ensure_file`` is a
deferred get-or-upload with ``skip``/``replace`` semantics.
"""

from __future__ import annotations

import io

import pytest
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport

_MISSING = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "The resource could not be found."}},
}

_FILE = {"d": {"Name": "report.txt", "ServerRelativeUrl": "/sites/x/Shared Documents/report.txt"}}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _sp(payloads):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _RecordingTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


def _root(ctx):
    return ctx.web.get_folder_by_server_relative_path("/sites/x/Shared Documents")


def _files(ctx):
    return _root(ctx).files


# --- FileCollection.upload_file ----------------------------------------------


def test_upload_file_large_path_uses_upload_session(tmp_path):
    ctx, transport = _sp([_FILE, _FILE, _FILE])
    source = tmp_path / "big.bin"
    source.write_bytes(b"0123456789")  # 10 bytes

    _files(ctx).upload_file(str(source), chunk_size=6).execute_query()

    # add + startUpload + finishUpload
    assert transport.calls == 3  # noqa: PLR2004
    urls = [request.url for request in transport.requests]
    assert any("startUpload" in url for url in urls)
    assert any("finishUpload" in url for url in urls)


def test_upload_file_small_stream():
    ctx, transport = _sp([_FILE])

    file = _files(ctx).upload_file(io.BytesIO(b"hi"), file_name="report.txt").execute_query()

    assert transport.calls == 1
    assert isinstance(file, File)


def test_upload_file_unnamed_stream_requires_name():
    ctx, transport = _sp([])

    with pytest.raises(ValueError):
        _files(ctx).upload_file(io.BytesIO(b"hi"))

    assert transport.calls == 0


def test_upload_file_reports_progress_for_simple_upload(tmp_path):
    ctx, _ = _sp([_FILE])
    source = tmp_path / "report.txt"
    source.write_bytes(b"hello")
    seen = []

    _files(ctx).upload_file(str(source), progress=seen.append).execute_query()

    assert seen and seen[-1].total == 5  # noqa: PLR2004


# --- Folder.ensure_file ------------------------------------------------------


def test_ensure_file_reuses_existing_without_reupload():
    ctx, transport = _sp([_FILE])

    file = _root(ctx).ensure_file("report.txt", b"hi").execute_query()

    assert transport.calls == 1  # probe only
    assert file.name == "report.txt"
    assert "Files('report.txt')" in str(file.resource_path)


def test_ensure_file_replace_overwrites_without_probe():
    ctx, transport = _sp([_FILE])

    file = _root(ctx).ensure_file("report.txt", b"hi", on_conflict="replace").execute_query()

    assert transport.calls == 1
    assert "/add" in transport.requests[0].url
    assert "Files('report.txt')" in str(file.resource_path)


def test_ensure_file_creates_parent_folders():
    ctx, transport = _sp([_FILE, _FILE, _MISSING, _FILE])

    _root(ctx).ensure_file("2026/Q1/report.txt", b"hi").execute_query()

    # folder 2026 + folder Q1 + probe + upload
    assert transport.calls == 4  # noqa: PLR2004


def test_ensure_file_large_content_uses_upload_session():
    ctx, transport = _sp([_MISSING, _FILE, _FILE, _FILE])

    _root(ctx).ensure_file("big.bin", b"0123456789", chunk_size=6).execute_query()

    # probe + add + startUpload + finishUpload
    assert transport.calls == 4  # noqa: PLR2004
    urls = [request.url for request in transport.requests]
    assert any("startUpload" in url for url in urls)
    assert any("finishUpload" in url for url in urls)
