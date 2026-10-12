"""Offline tests for Planner optimistic concurrency and top-level item routing.

Graph enforces ``If-Match`` on Planner updates/deletes and only accepts item
reads/writes plus creation at the top-level ``/planner/buckets`` and
``/planner/tasks`` endpoints (listing stays nested under the plan). These tests
pin both behaviours without touching the network.
"""

from __future__ import annotations

from urllib.parse import unquote_plus

import pytest
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


def test_consecutive_updates_track_the_latest_etag():
    client, transport = _client(
        [
            {"http_status": 200, "headers": {"ETag": ETAG}, "body": PLAN},
            {"http_status": 200, "headers": {"ETag": 'W/"etag-2"'}, "body": {"id": "p1"}},
            {"http_status": 200, "headers": {"ETag": 'W/"etag-3"'}, "body": {"id": "p1"}},
        ]
    )
    plan = client.planner.plans["p1"].get().execute_query()

    plan.title = "First"
    plan.update().execute_query()
    plan.title = "Second"
    plan.update().execute_query()

    assert transport.requests[-2].headers.get("If-Match") == ETAG
    assert transport.requests[-1].headers.get("If-Match") == 'W/"etag-2"'


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


def test_nested_bucket_add_posts_to_top_level_endpoint():
    client, transport = _client(
        [
            {"http_status": 200, "headers": {}, "body": PLAN},
            {
                "http_status": 201,
                "headers": {"ETag": 'W/"b1"'},
                "body": {"id": "b1", "name": "Backlog", "planId": "p1"},
            },
        ]
    )
    plan = client.planner.plans["p1"].get().execute_query()

    bucket = plan.buckets.add("Backlog").execute_query()

    create = transport.requests[-1]
    assert create.method == HttpMethod.Post
    assert create.url.endswith("/planner/buckets")
    assert create.data["name"] == "Backlog"
    assert create.data["planId"] == "p1"
    assert bucket.resource_path.to_url().endswith("/planner/buckets/b1")


def test_listed_bucket_update_targets_top_level_item_path():
    client, transport = _client(
        [
            {"http_status": 200, "headers": {}, "body": PLAN},
            {
                "http_status": 200,
                "headers": {},
                "body": {"value": [{"id": "b1", "name": "Backlog", "@odata.etag": 'W/"b1"'}]},
            },
            {
                "http_status": 200,
                "headers": {"ETag": 'W/"b2"'},
                "body": {"id": "b1", "name": "Backlog (renamed)"},
            },
        ]
    )
    plan = client.planner.plans["p1"].get().execute_query()

    listed = plan.buckets.get().execute_query()
    listed_bucket = list(listed)[0]
    assert "/planner/plans/p1/buckets" in unquote_plus(transport.requests[-1].url)

    listed_bucket.name = "Backlog (renamed)"
    listed_bucket.update().execute_query()

    patch = transport.requests[-1]
    assert patch.method == HttpMethod.Patch
    assert patch.url.endswith("/planner/buckets/b1")
    assert patch.headers.get("If-Match") == 'W/"b1"'
    assert listed_bucket.properties.get("__etag") == 'W/"b2"'


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


@pytest.mark.parametrize(
    ("attribute", "expected"),
    [("tasks", "/planner/plans/p1/tasks"), ("buckets", "/planner/plans/p1/buckets")],
)
def test_nested_collection_listing_stays_under_the_plan(attribute, expected):
    client, transport = _client(
        [
            {"http_status": 200, "headers": {}, "body": PLAN},
            {"http_status": 200, "headers": {}, "body": {"value": []}},
        ]
    )
    plan = client.planner.plans["p1"].get().execute_query()

    getattr(plan, attribute).get().execute_query()

    assert expected in unquote_plus(transport.requests[-1].url)


def test_item_addressing_uses_the_top_level_set():
    client = GraphClient()
    plan = client.planner.plans["p1"]

    # Listing is scoped to the plan, but each item lives in the top-level set.
    assert plan.buckets.resource_path.to_url() == "/planner/plans/p1/buckets"
    assert plan.buckets["b1"].resource_path.to_url() == "/planner/buckets/b1"
    assert plan.tasks["t1"].resource_path.to_url() == "/planner/tasks/t1"
