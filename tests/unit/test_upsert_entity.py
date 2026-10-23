"""Offline tests for the server-side upsert query (``PATCH`` + ``Prefer``).

``Entity.upsert()`` issues a ``PATCH`` carrying
``Prefer: create-if-missing, return=representation`` against an alternate-key
resource and surfaces ``UpsertNotSupported`` when the service answers as if the
preference were ignored, so the caller can fall back to a client-side reconcile.
"""

from __future__ import annotations

import pytest
from office365.graph_client import GraphClient
from office365.runtime.exceptions import AccessDeniedException, UpsertNotSupported
from office365.runtime.http.http_method import HttpMethod
from tests._scripted_transport import ScriptedTransport


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


def _ok(body):
    return {"http_status": 200, "body": body}


def test_upsert_issues_patch_with_prefer_and_returns_representation():
    client, transport = _client([_ok({"id": "g1", "displayName": "Group157", "description": "Desc"})])

    group = client.groups.get_by_alternate_key("uniqueName", "Group157")
    group.set_property("description", "Desc")
    group.upsert().execute_query()

    request = transport.requests[0]
    assert request.method == HttpMethod.Patch
    assert request.headers["Prefer"] == "create-if-missing, return=representation"
    assert request.data["description"] == "Desc"
    assert group.id == "g1"
    assert group.get_property("displayName") == "Group157"


def test_upsert_sets_conditional_headers_only_when_given():
    client, transport = _client([_ok({"id": "g1"}), _ok({"id": "g1"})])

    group = client.groups.get_by_alternate_key("uniqueName", "Group157")
    group.upsert(if_match='W/"etag-1"').execute_query()
    group.upsert(if_none_match="*").execute_query()

    assert transport.requests[0].headers["If-Match"] == 'W/"etag-1"'
    assert "If-None-Match" not in transport.requests[0].headers
    assert transport.requests[1].headers["If-None-Match"] == "*"
    assert "If-Match" not in transport.requests[1].headers


def test_upsert_400_naming_the_preference_is_translated_to_not_supported():
    client, _ = _client(
        [
            {
                "http_status": 400,
                "body": {"error": {"code": "BadRequest", "message": "Prefer: create-if-missing is not supported"}},
            }
        ]
    )

    group = client.groups.get_by_alternate_key("uniqueName", "Missing")
    with pytest.raises(UpsertNotSupported):
        group.upsert().execute_query()


def test_upsert_denied_propagates_access_denied():
    client, _ = _client([("deny",)])

    group = client.groups.get_by_alternate_key("uniqueName", "Group157")
    with pytest.raises(AccessDeniedException):
        group.upsert().execute_query()
