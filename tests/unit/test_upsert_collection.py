"""Offline tests for the unified single-entity ``upsert`` verb.

``RecordCollection.upsert`` reconciles client-side: a tolerant ``$filter``
lookup, then a create when missing or a write-idempotent update when present.
The create runs in the lookup's queue slot (via a barrier), so anything queued
after the upsert still runs after the resource exists.
"""

from __future__ import annotations

import pytest
from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.odata.literals import odata_literal
from tests._scripted_transport import ScriptedTransport

_EXISTING = {"id": "g1", "displayName": "Group157", "description": "Old"}
_CREATED = {"id": "g1", "displayName": "Group157", "description": "Team site"}


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


def _methods(transport):
    return [request.method for request in transport.requests]


# ── odata_literal ────────────────────────────────────────────────


def test_odata_literal_quotes_strings_and_escapes_quotes():
    assert odata_literal("Group157") == "'Group157'"
    assert odata_literal("O'Brien") == "'O''Brien'"


def test_odata_literal_emits_numbers_booleans_and_null_bare():
    assert odata_literal(42) == "42"
    assert odata_literal(True) == "true"
    assert odata_literal(False) == "false"
    assert odata_literal(None) == "null"


# ── upsert: create when missing ──────────────────────────────────


def test_upsert_creates_when_missing():
    client, transport = _client([{"value": []}, _CREATED])

    group = client.groups.upsert("uniqueName", "Group157", displayName="Group157", description="Team site")
    group.execute_query()

    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Post]
    assert "uniqueName eq 'Group157'" in transport.requests[0].url
    assert transport.requests[1].url.endswith("/groups")
    assert transport.requests[1].data == {
        "uniqueName": "Group157",
        "displayName": "Group157",
        "description": "Team site",
    }
    assert group.id == "g1"
    assert group.display_name == "Group157"


def test_upsert_creates_with_only_the_key_when_no_properties():
    client, transport = _client([{"value": []}, {"id": "g1", "uniqueName": "Group157"}])

    group = client.groups.upsert("uniqueName", "Group157").execute_query()

    assert transport.requests[1].data == {"uniqueName": "Group157"}
    assert group.is_loaded


def test_upsert_skip_still_creates_when_missing():
    client, transport = _client([{"value": []}, _CREATED])

    client.groups.upsert("uniqueName", "Group157", on_conflict="skip", description="Team site").execute_query()

    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Post]


# ── upsert: reconcile when present ───────────────────────────────


def test_upsert_updates_changed_properties():
    client, transport = _client([{"value": [_EXISTING]}, _EXISTING])

    group = client.groups.upsert("uniqueName", "Group157", description="New").execute_query()

    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Patch]
    assert transport.requests[1].url.endswith("/groups/g1")
    assert transport.requests[1].data["description"] == "New"
    assert group.id == "g1"


def test_upsert_is_write_idempotent_when_state_matches():
    client, transport = _client([{"value": [_EXISTING]}])

    group = client.groups.upsert("uniqueName", "Group157", description="Old").execute_query()

    assert _methods(transport) == [HttpMethod.Get]
    assert group.id == "g1"
    assert group.description == "Old"


def test_upsert_skip_leaves_existing_untouched():
    client, transport = _client([{"value": [_EXISTING]}])

    group = client.groups.upsert("uniqueName", "Group157", on_conflict="skip", description="New").execute_query()

    assert _methods(transport) == [HttpMethod.Get]
    assert group.description == "Old"


def test_upsert_does_not_update_when_no_properties_requested():
    client, transport = _client([{"value": [_EXISTING]}])

    client.groups.upsert("uniqueName", "Group157").execute_query()

    assert _methods(transport) == [HttpMethod.Get]


# ── upsert: identity formatting ──────────────────────────────────


def test_upsert_escapes_the_string_key_value():
    client, transport = _client([{"value": []}, _CREATED])

    client.groups.upsert("displayName", "O'Brien", description="Team site").execute_query()

    assert "displayName eq 'O''Brien'" in transport.requests[0].url


def test_upsert_supports_an_integer_key():
    client, transport = _client([{"value": []}, {"id": 7, "displayName": "Seven"}])

    client.groups.upsert("id", 7, displayName="Seven").execute_query()

    assert "id eq 7" in transport.requests[0].url
    assert transport.requests[1].data == {"id": 7, "displayName": "Seven"}


# ── upsert: deferred ordering ────────────────────────────────────


def test_upsert_create_runs_before_queries_queued_after_it():
    client, transport = _client([{"value": []}, _CREATED, _CREATED])

    group = client.groups.upsert("uniqueName", "Group157", description="Team site")
    group.get()  # dependent read queued after the upsert
    group.execute_query()

    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Post, HttpMethod.Get]
    assert transport.requests[1].url.endswith("/groups")
    assert transport.requests[2].url.endswith("/groups/g1")


def test_upsert_rejects_retired_on_conflict_value():
    client, _ = _client([])

    with pytest.raises(ValueError, match="on_conflict"):
        client.groups.upsert("uniqueName", "Group157", on_conflict="upsert")


# ── upsert: SharePoint parity ────────────────────────────────────


def _sp(payloads):
    from office365.sharepoint.client_context import ClientContext
    from tests import test_site_url

    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _RecordingTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


def test_upsert_creates_list_when_missing():
    ctx, transport = _sp([{"d": {"results": []}}, {"d": {"Id": "list-1", "Title": "Documents"}}])

    result = ctx.web.lists.upsert("Title", "Documents").execute_query()

    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Post]
    assert "Title eq 'Documents'" in transport.requests[0].url
    assert transport.requests[1].data == {"Title": "Documents"}
    assert result.get_property("Id") == "list-1"


def test_upsert_updates_existing_list():
    ctx, transport = _sp([{"d": {"results": [{"Id": "list-1", "Title": "Documents", "Description": "Old"}]}}, {}])

    result = ctx.web.lists.upsert("Title", "Documents", Description="New").execute_query()

    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Post]
    assert transport.requests[1].headers["X-HTTP-Method"] == "MERGE"
    assert "Description" in transport.requests[1].data
    assert result.get_property("Description") == "New"


def test_upsert_is_write_idempotent_for_sharepoint():
    ctx, transport = _sp([{"d": {"results": [{"Id": "list-1", "Title": "Documents", "Description": "Old"}]}}])

    ctx.web.lists.upsert("Title", "Documents", Description="Old").execute_query()

    assert _methods(transport) == [HttpMethod.Get]
