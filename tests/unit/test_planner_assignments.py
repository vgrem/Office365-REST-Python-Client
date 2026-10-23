"""Offline tests for Planner assignments and checklists.

Both are Open Types keyed by id: assignments per user id, checklists per item
id. ``null`` values remove entries. These tests pin the wire format (including
the server-managed identity fields that must not be sent back) without network.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.planner.tasks.task import PlannerTask
from office365.planner.tasks.task_details import PlannerTaskDetails
from office365.runtime.odata.v4.json_format import V4JsonFormat

TASK = {"id": "t1", "title": "Do it", "@odata.etag": 'W/"t1"'}


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


def test_checklist_add_and_remove_serialize_by_item_id():
    details = PlannerTaskDetails(GraphClient(), None)
    item_id = details.add_checklist_item("Draft", is_checked=True).checklist.add("Review")

    body = details.to_json(V4JsonFormat())["checklist"]
    assert body[item_id]["title"] == "Review"
    assert body[item_id]["isChecked"] is False
    assert "lastModifiedBy" not in body[item_id]

    details.checklist.remove(item_id)
    assert details.to_json(V4JsonFormat())["checklist"][item_id] is None
