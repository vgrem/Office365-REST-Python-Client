"""Offline tests for the Microsoft To Do model and payload builders.

The Graph To Do service resolves ``@odata.type`` against the ``microsoft.graph``
namespace and requires ``displayName`` when creating a list, so these tests pin
the payload shapes that the live service accepts:

- ``TodoTaskListCollection.ensure`` must send ``displayName`` on create;
- ``TaskFileAttachment`` must advertise the ``taskFileAttachment`` OData type;
- ``LinkedResource`` must **not** advertise a type the service cannot resolve.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.todo.attachments.base import AttachmentBase
from office365.todo.attachments.task_file import TaskFileAttachment
from office365.todo.linked_resource import LinkedResource
from tests._scripted_transport import ScriptedTransport


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


def test_ensure_sends_display_name_when_list_is_missing():
    transport = _RecordingTransport([{"value": []}, {"id": "1", "displayName": "Groceries"}])
    client = _client(transport)

    task_list = client.me.todo.lists.ensure("Groceries").execute_query()

    assert task_list.display_name == "Groceries"
    assert [request.method for request in transport.requests] == [HttpMethod.Get, HttpMethod.Post]
    assert transport.requests[1].url.endswith("/lists")
    assert transport.requests[1].data["displayName"] == "Groceries"


def test_ensure_reuses_existing_list_without_creating():
    transport = _RecordingTransport([{"value": [{"id": "1", "displayName": "Groceries"}]}])
    client = _client(transport)

    task_list = client.me.todo.lists.ensure("Groceries").execute_query()

    assert task_list.display_name == "Groceries"
    assert len(transport.requests) == 1
    assert transport.requests[0].method == HttpMethod.Get


def test_task_file_attachment_advertises_odata_type():
    attachment = TaskFileAttachment(None)
    attachment.set_property("name", "note.txt")
    attachment.set_property("contentBytes", "aGk=")

    assert attachment.entity_type_name == "microsoft.graph.taskFileAttachment"
    assert attachment.to_json(V4JsonFormat())["@odata.type"] == "#microsoft.graph.taskFileAttachment"


def test_linked_resource_omits_unresolvable_odata_type():
    resource = LinkedResource(None)
    resource.set_property("applicationName", "Outlook")

    assert resource.entity_type_name is None
    assert "@odata.type" not in resource.to_json(V4JsonFormat())


def test_attachment_base_exposes_content_bytes():
    attachment = AttachmentBase(None)
    attachment.set_property("contentBytes", "aGk=")

    assert attachment.content_bytes == "aGk="
    assert AttachmentBase(None).content_bytes is None
