"""Offline tests for Planner optimistic concurrency and top-level item routing.

Graph enforces ``If-Match`` on Planner updates/deletes and only accepts item
reads/writes plus creation at the top-level ``/planner/buckets`` and
``/planner/tasks`` endpoints (listing stays nested under the plan). These tests
pin both behaviours without touching the network.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from tests._scripted_transport import ScriptedTransport

PLAN = {"id": "p1", "title": "Roadmap", "@odata.etag": 'W/"etag-1"'}
ETAG = 'W/"etag-1"'


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the outgoing request objects."""

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


def test_plan_update_sends_if_match_and_refreshes_etag():
    client, transport = _client(
        [
            {"http_status": 200, "headers": {"ETag": ETAG}, "body": PLAN},
            {
                "http_status": 200,
                "headers": {"ETag": 'W/"etag-2"'},
                "body": {"id": "p1", "title": "Roadmap v2"},
            },
        ]
    )
    plan = client.planner.plans["p1"].get().execute_query()

    plan.title = "Roadmap v2"
    plan.update().execute_query()

    update = transport.requests[-1]
    assert update.method == HttpMethod.Patch
    assert update.headers.get("If-Match") == ETAG
    assert update.headers.get("Prefer") == "return=representation"
    # The new etag comes back in the ``ETag`` header (the PATCH body is empty),
    # so a chained update/delete no longer hits a stale-token 409.
    assert plan.properties.get("__etag") == 'W/"etag-2"'


def test_plan_delete_sends_if_match():
    client, transport = _client(
        [
            {"http_status": 200, "headers": {"ETag": ETAG}, "body": PLAN},
            {"http_status": 204, "headers": {}, "body": None},
        ]
    )
    plan = client.planner.plans["p1"].get().execute_query()

    plan.delete_object().execute_query()

    delete = transport.requests[-1]
    assert delete.method == HttpMethod.Delete
    assert delete.headers.get("If-Match") == ETAG


def test_nested_task_add_posts_to_top_level_endpoint():
    client, transport = _client(
        [
            {"http_status": 200, "headers": {}, "body": PLAN},
            {
                "http_status": 201,
                "headers": {"ETag": 'W/"t1"'},
                "body": {"id": "t1", "title": "Do it", "planId": "p1"},
            },
        ]
    )
    plan = client.planner.plans["p1"].get().execute_query()

    task = plan.tasks.add("Do it").execute_query()

    create = transport.requests[-1]
    assert create.method == HttpMethod.Post
    assert create.url.endswith("/planner/tasks")
    assert create.data["title"] == "Do it"
    assert create.data["planId"] == "p1"
    assert task.resource_path.to_url().endswith("/planner/tasks/t1")
