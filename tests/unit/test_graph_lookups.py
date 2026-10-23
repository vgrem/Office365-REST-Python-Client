"""Offline tests for the Graph ``find_by_*`` lookup helpers.

Every lookup is *deferred* (nothing hits the wire until ``execute_query()``) and
*tolerant* by default: a miss leaves the returned entity uninitialized instead
of raising, detected via ``is_loaded``. Pass ``required=True`` for the strict
``single`` semantics.
"""

from __future__ import annotations

from urllib.parse import unquote_plus

import pytest
from office365.graph_client import GraphClient
from office365.runtime.types.exceptions import NotFoundException
from tests._scripted_transport import ScriptedTransport

USER = {"id": "u1", "displayName": "Ada Lovelace", "mail": "ada@contoso.com"}
TODO_TASK = {"id": "tt1", "title": "Ship the release"}
MAIL_FOLDER = {"id": "mf1", "displayName": "Archive"}
NOTEBOOK = {"id": "nb1", "displayName": "SDK OneNote Tour"}
SECTION = {"id": "sec1", "displayName": "SDK Examples"}
PLANNER_TASK = {"id": "pkt1", "title": "Draft the plan"}
PLANNER_BUCKET = {"id": "pbk1", "name": "Backlog"}
TEAM = {"id": "g1", "displayName": "Team One", "resourceProvisioningOptions": ["Team"]}
BUSINESS = {"id": "b1", "displayName": "Contoso Bookings"}
DEVICE = {"id": "d1", "deviceName": "DESKTOP-1"}
SKU = {"id": "s1", "skuId": "sku-guid", "skuPartNumber": "ENTERPRISEPACK"}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the request URLs it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.urls: list[str] = []

    def execute(self, request):
        self.urls.append(request.url)
        return super().execute(request)


def _client(payloads):
    transport = _RecordingTransport(payloads)
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client, transport


@pytest.mark.parametrize(
    ("lookup", "key", "payload"),
    [
        (lambda client: client.users.find_by_mail, "nobody@contoso.com", {"value": []}),
        (lambda client: client.teams.find_by_name, "Missing Team", {"value": []}),
        (lambda client: client.device_management.managed_devices.find_by_name, "NOPE", {"value": []}),
        (lambda client: client.subscribed_skus.find_by_part_number, "NOT_A_SKU", {"value": [SKU]}),
    ],
)
def test_lookup_miss_leaves_entity_uninitialized(lookup, key, payload):
    client, _ = _client([payload])

    entity = lookup(client)(key).execute_query()

    assert not entity.is_loaded
    assert entity.get_property("id") is None


@pytest.mark.parametrize(
    ("lookup", "key", "payload", "entity_id", "path", "filter_fragment"),
    [
        (
            lambda c: c.me.todo.lists["l1"].tasks.find_by_title,
            "Ship the release",
            TODO_TASK,
            "tt1",
            "/me/todo/lists/l1/tasks",
            "title eq 'Ship the release'",
        ),
        (
            lambda c: c.me.mail_folders.find_by_display_name,
            "Archive",
            MAIL_FOLDER,
            "mf1",
            "/me/mailFolders",
            "displayName eq 'Archive'",
        ),
        (
            lambda c: c.me.onenote.notebooks.find_by_display_name,
            "SDK OneNote Tour",
            NOTEBOOK,
            "nb1",
            "/me/onenote/notebooks",
            "displayName eq 'SDK OneNote Tour'",
        ),
        (
            lambda c: c.me.onenote.sections.find_by_display_name,
            "SDK Examples",
            SECTION,
            "sec1",
            "/me/onenote/sections",
            "displayName eq 'SDK Examples'",
        ),
    ],
)
def test_named_find_by_defers_and_returns_match(lookup, key, payload, entity_id, path, filter_fragment):
    client, transport = _client([{"value": [payload]}])

    entity = lookup(client)(key)

    assert transport.urls == []
    assert not entity.is_loaded

    entity.execute_query()

    assert entity.is_loaded
    assert entity.get_property("id") == entity_id
    url = unquote_plus(transport.urls[0])
    assert path in url
    assert filter_fragment in url


def test_team_find_by_name_required_raises_on_miss():
    client, _ = _client([{"value": []}])

    client.teams.find_by_name("Missing Team", required=True)

    with pytest.raises(NotFoundException):
        client.execute_query()
