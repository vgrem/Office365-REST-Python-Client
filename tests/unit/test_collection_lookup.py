"""Offline tests for ``ClientObjectCollection.first`` / ``single``.

``single`` must bound its query to ``$top=2`` so an ambiguous match is rejected
without downloading every matching item, while ``first`` stays at ``$top=1``.
"""

from __future__ import annotations

import pytest
from office365.graph_client import GraphClient
from tests._scripted_transport import ScriptedTransport

GROUP = {"id": "g1", "displayName": "Group One"}


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


def test_single_bounds_query_with_top_2():
    client, transport = _client([{"value": [GROUP]}])

    client.groups.single("displayName eq 'Group One'")
    client.execute_query()

    assert len(transport.urls) == 1
    assert "$top=2" in transport.urls[0]


def test_find_by_name_queues_a_tolerant_read():
    """``find_by_name`` is tolerant by default and queues its own read.

    The match is copied into the returned object and its path is anchored at
    ``/groups/{id}``; a trailing ``.get()`` would therefore issue a redundant
    second request.
    """
    client, transport = _client([{"value": [GROUP]}])

    group = client.groups.find_by_name("Group One").execute_query()

    assert len(transport.urls) == 1
    assert "$filter=displayName eq 'Group One'" in transport.urls[0]
    assert group.is_loaded
    assert str(group.resource_path) == "/groups/g1"


def test_find_by_name_required_raises_on_ambiguous():
    client, _ = _client([{"value": [GROUP, {"id": "g2", "displayName": "Group One"}]}])

    client.groups.find_by_name("Group One", required=True)

    with pytest.raises(ValueError):
        client.execute_query()


def test_get_by_principal_name_is_a_bare_address():
    """Contrast: ``get_by_principal_name`` only addresses the entity.

    Nothing is queued on its own, so ``.get()`` is required to fetch it — the
    examples that resolve a user by UPN must keep the trailing ``.get()``.
    """
    client, transport = _client([{"id": "u1", "userPrincipalName": "a@contoso.com"}])

    user = client.users.get_by_principal_name("a@contoso.com").execute_query()

    assert transport.urls == []
    assert not user.is_loaded
    assert str(user.resource_path) == "/users/a@contoso.com"

    user.get().execute_query()

    assert len(transport.urls) == 1
    assert user.is_loaded


def test_directory_role_lookup_skips_unsupported_top():
    """``directoryRoles`` rejects custom page sizes, so the lookup must not send ``$top``.

    The bound is enforced client-side instead of letting the server reject the
    request with ``Request_UnsupportedQuery``.
    """
    payload = {
        "value": [
            {"id": "r2", "displayName": "Helpdesk Administrator"},
        ]
    }
    client, transport = _client([payload])

    role = client.directory_roles.find_by_name("Helpdesk Administrator", required=True).execute_query()

    assert len(transport.urls) == 1
    assert "$top" not in transport.urls[0]
    assert "$filter=displayName eq 'Helpdesk Administrator'" in transport.urls[0]
    assert role.get_property("id") == "r2"
    assert str(role.resource_path) == "/directoryRoles/r2"
