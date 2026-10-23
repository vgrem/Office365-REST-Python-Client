"""Offline tests for the multipart body built by ``OnenotePageCollection.add``.

OneNote creates a page from a ``multipart/form-data`` request: the page HTML as
the ``Presentation`` part, plus one part per embedded image/file, each referenced
by name from the HTML. The collection accepts a file-like object (whose ``.name``
selects the MIME type), raw ``bytes``, or a plain ``str``, so callers do not have
to wrap HTML in ``BytesIO`` just to create a page.
"""

from __future__ import annotations

import io

from office365.graph_client import GraphClient
from tests._scripted_transport import ScriptedTransport

_PAGE = {"id": "page-1", "title": "Notes"}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _client(transport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def _pages(client):
    """The ``pages`` collection of a section — an ``OnenotePageCollection``."""
    return client.me.onenote.sections["section-1"].pages


def test_add_accepts_html_string():
    transport = _RecordingTransport([_PAGE])
    client = _client(transport)

    page = _pages(client).add(presentation_file="<html><head><title>Notes</title></head><body/></html>").execute_query()

    request = transport.requests[-1]
    assert str(request.method) == "POST"
    assert request.url.endswith("/onenote/sections/section-1/pages")
    assert "multipart/form-data; boundary=" in request.headers["Content-Type"]
    assert b'name="Presentation"' in request.data
    assert b"text/html" in request.data
    assert b"<html>" in request.data
    assert page.get_property("id") == "page-1"


def test_add_accepts_bytes_and_named_file_attachments():
    transport = _RecordingTransport([_PAGE])
    client = _client(transport)

    image = io.BytesIO(b"\x89PNG fake bytes")
    image.name = "chart.png"

    _pages(client).add(
        presentation_file=b"<html/>",
        attachment_files={"imageBlock1": image, "fileBlock1": b"raw-byte payload"},
    ).execute_query()

    body = transport.requests[-1].data
    assert b'name="imageBlock1"' in body
    assert b"image/png" in body
    assert b"fake bytes" in body
    assert b'name="fileBlock1"' in body
    assert b"application/octet-stream" in body
    assert b"raw-byte payload" in body
