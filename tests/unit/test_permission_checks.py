"""Offline tests for the ``GraphClient`` permission-check helpers.

``has_application_permissions`` resolves the app roles assigned to a client
service principal and answers eagerly, mirroring ``require_application_permission``.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from tests._scripted_transport import ScriptedTransport

GRAPH_SP = {"id": "graph-sp", "displayName": "Microsoft Graph"}
CLIENT_SP = {"id": "client-sp"}
GRAPH_SP_WITH_ROLES = {
    "id": "graph-sp",
    "appRoles": [{"id": "role-1", "value": "User.Read.All", "displayName": "Read users"}],
    "appRoleAssignedTo": [
        {"id": "assign-1", "appRoleId": "role-1", "principalId": "client-sp", "resourceId": "graph-sp"}
    ],
}


def _client(payloads):
    transport = ScriptedTransport(payloads)
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client, transport


def test_has_application_permissions_true_when_role_assigned():
    client, _ = _client([{"value": [GRAPH_SP]}, GRAPH_SP_WITH_ROLES, CLIENT_SP])

    granted = client.has_application_permissions("User.Read.All", "app-guid")

    assert granted is True
