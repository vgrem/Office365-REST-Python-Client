"""Offline tests for the collection ``ensure`` helpers.

Two flavours are covered:

* **create-first** (OneNote notebooks/sections, Outlook mail folders) — the
  server rejects a duplicate name, the library classifies that as
  :class:`~office365.runtime.exceptions.DuplicatedObjectException`, and the
  create-first ``create_or_get`` helper falls back to a lookup.
* **filter-first** (To Do tasks, whose titles are not unique) — the lookup runs
  first and only an empty result creates the object.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from tests._scripted_transport import ScriptedTransport

_NOTEBOOK = {"id": "nb-1", "displayName": "SDK OneNote Tour"}
_SECTION = {"id": "sec-1", "displayName": "SDK Examples"}
_FOLDER = {"id": "folder-1", "displayName": "Archive"}
_TASK = {"id": "task-1", "title": "Prepare the demo"}

_ONENOTE_DUPLICATE = {
    "http_status": 400,
    "body": {
        "error": {
            "code": "20117",
            "message": "An item with this name already exists in this location.",
        }
    },
}
_FOLDER_DUPLICATE = {
    "http_status": 400,
    "body": {
        "error": {
            "code": "ErrorFolderExists",
            "message": "A folder with the specified name already exists.",
        }
    },
}


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


def _methods(transport: _RecordingTransport) -> list[str]:
    return [request.method for request in transport.requests]


def test_notebook_ensure_creates_when_missing():
    transport = _RecordingTransport([_NOTEBOOK])
    client = _client(transport)

    notebook = client.me.onenote.notebooks.ensure("SDK OneNote Tour").execute_query()

    assert notebook.display_name == "SDK OneNote Tour"
    assert _methods(transport) == [HttpMethod.Post]
    assert transport.requests[0].url.endswith("/me/onenote/notebooks")
    assert transport.requests[0].data["displayName"] == "SDK OneNote Tour"


def test_notebook_ensure_reuses_existing():
    transport = _RecordingTransport([_ONENOTE_DUPLICATE, {"value": [_NOTEBOOK]}])
    client = _client(transport)

    notebook = client.me.onenote.notebooks.ensure("SDK OneNote Tour").execute_query()

    assert notebook.id == "nb-1"
    assert _methods(transport) == [HttpMethod.Post, HttpMethod.Get]
    assert "displayName eq 'SDK OneNote Tour'" in transport.requests[1].url


def test_section_ensure_creates_when_missing():
    transport = _RecordingTransport([_SECTION])
    client = _client(transport)

    section = client.me.onenote.sections.ensure("SDK Examples").execute_query()

    assert section.display_name == "SDK Examples"
    assert _methods(transport) == [HttpMethod.Post]
    assert transport.requests[0].data["displayName"] == "SDK Examples"


def test_section_ensure_scoped_to_notebook_reuses_existing():
    transport = _RecordingTransport([_ONENOTE_DUPLICATE, {"value": [_SECTION]}])
    client = _client(transport)

    section = client.me.onenote.notebooks["nb-1"].sections.ensure("SDK Examples").execute_query()

    assert section.id == "sec-1"
    assert _methods(transport) == [HttpMethod.Post, HttpMethod.Get]
    assert transport.requests[0].url.endswith("/me/onenote/notebooks/nb-1/sections")


def test_mail_folder_ensure_creates_when_missing():
    transport = _RecordingTransport([_FOLDER])
    client = _client(transport)

    folder = client.me.mail_folders.ensure("Archive").execute_query()

    assert folder.display_name == "Archive"
    assert _methods(transport) == [HttpMethod.Post]
    assert transport.requests[0].data["displayName"] == "Archive"


def test_mail_folder_ensure_reuses_existing():
    transport = _RecordingTransport([_FOLDER_DUPLICATE, {"value": [_FOLDER]}])
    client = _client(transport)

    folder = client.me.mail_folders["inbox"].child_folders.ensure("Archive").execute_query()

    assert folder.id == "folder-1"
    assert _methods(transport) == [HttpMethod.Post, HttpMethod.Get]
    assert transport.requests[0].url.endswith("/me/mailFolders/inbox/childFolders")


def test_todo_task_ensure_creates_when_missing():
    transport = _RecordingTransport([{"value": []}, _TASK])
    client = _client(transport)

    task = client.me.todo.lists["list-1"].tasks.ensure("Prepare the demo").execute_query()

    assert task.title == "Prepare the demo"
    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Post]
    assert "title eq 'Prepare the demo'" in transport.requests[0].url
    assert transport.requests[1].data["title"] == "Prepare the demo"


def test_todo_task_ensure_reuses_existing():
    transport = _RecordingTransport([{"value": [_TASK]}])
    client = _client(transport)

    task = client.me.todo.lists["list-1"].tasks.ensure("Prepare the demo").execute_query()

    assert task.id == "task-1"
    assert _methods(transport) == [HttpMethod.Get]


_DOMAIN = {"id": "contoso.com", "isDefault": False, "isVerified": False}
_DOMAIN_404 = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "Domain not found."}},
}


def test_domain_ensure_creates_when_missing():
    transport = _RecordingTransport([_DOMAIN_404, _DOMAIN])
    client = _client(transport)

    domain = client.domains.ensure("contoso.com").execute_query()

    assert domain.id == "contoso.com"
    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Post]
    assert transport.requests[0].url.endswith("/domains/contoso.com")
    assert transport.requests[1].url.endswith("/domains")
    assert transport.requests[1].data["id"] == "contoso.com"


def test_domain_ensure_reuses_existing():
    transport = _RecordingTransport([_DOMAIN])
    client = _client(transport)

    domain = client.domains.ensure("contoso.com").execute_query()

    assert domain.id == "contoso.com"
    assert _methods(transport) == [HttpMethod.Get]
    assert transport.requests[0].url.endswith("/domains/contoso.com")
