"""Offline tests for Planner assignments and checklists.

Both are Open Types keyed by id: assignments per user id, checklists per item
id. ``null`` values remove entries. These tests pin the wire format (including
the server-managed identity fields that must not be sent back) without network.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.planner.tasks.task import PlannerTask
from office365.planner.tasks.task_details import PlannerTaskDetails
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.odata.v4.json_format import V4JsonFormat
from tests._scripted_transport import ScriptedTransport

TASK = {"id": "t1", "title": "Do it", "@odata.etag": 'W/"t1"'}


class _RecordingTransport(ScriptedTransport):
    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _client(payloads):
    transport = _RecordingTransport(payloads)
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client, transport


def test_assignments_deserialize_to_typed_values():
    task = PlannerTask(GraphClient())
    task.set_property(
        "assignments",
        {"u-9": {"orderHint": " !", "assignedDateTime": "2024-01-01T00:00:00Z"}},
        False,
    )

    ((user_id, assignment),) = list(task.assignments)
    assert user_id == "u-9"
    assert assignment.orderHint == " !"
    assert assignment.assignedDateTime is not None


def test_assign_and_update_sends_if_match_and_refreshes_etag():
    client, transport = _client(
        [
            {"http_status": 200, "headers": {"ETag": 'W/"t1"'}, "body": TASK},
            {"http_status": 200, "headers": {"ETag": 'W/"t2"'}, "body": {"id": "t1"}},
        ]
    )
    task = client.planner.tasks["t1"].get().execute_query()

    task.assign_to("u-1").update().execute_query()

    update = transport.requests[-1]
    assert update.method == HttpMethod.Patch
    assert update.headers.get("If-Match") == 'W/"t1"'
    assert update.headers.get("Prefer") == "return=representation"
    assert update.data["assignments"]["u-1"]["orderHint"] == " !"
    assert task.properties.get("__etag") == 'W/"t2"'


def test_checklist_add_and_remove_serialize_by_item_id():
    details = PlannerTaskDetails(GraphClient(), None)
    item_id = details.add_checklist_item("Draft", is_checked=True).checklist.add("Review")

    body = details.to_json(V4JsonFormat())["checklist"]
    assert body[item_id]["title"] == "Review"
    assert body[item_id]["isChecked"] is False
    assert "lastModifiedBy" not in body[item_id]

    details.checklist.remove(item_id)
    assert details.to_json(V4JsonFormat())["checklist"][item_id] is None


def test_set_checklist_replaces_loaded_items():
    details = PlannerTaskDetails(GraphClient(), None)
    details.set_property(
        "checklist",
        {"old": {"title": "Old", "isChecked": False, "orderHint": " !"}},
        False,
    )

    details.set_checklist(["One", "Two"])

    checklist = details.to_json(V4JsonFormat())["checklist"]
    assert checklist["old"] is None
    titles = {v["title"] for k, v in checklist.items() if v is not None}
    assert titles == {"One", "Two"}
