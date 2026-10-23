"""Offline tests for the idempotent application-permission grant helpers.

Covers ``ServicePrincipal.grant_application_permissions`` (grant an app role to a
client app on a resource, re-run safe) and the app-centric
``Application.grant_permissions`` / ``Application.revoke_permissions`` that resolve
the resource service principal and delegate to it.
"""

from __future__ import annotations

from office365.directory.permissions.resource_name import ResourceName
from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from tests._scripted_transport import ScriptedTransport

CLIENT_APP_ID = "11111111-1111-1111-1111-111111111111"
CLIENT_OBJECT_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"
CLIENT_SP_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
SHAREPOINT_APP_ID = "00000003-0000-0ff1-ce00-000000000000"
SHAREPOINT_SP_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
ROLE_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
OTHER_ROLE_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff"
ASSIGNMENT_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"

APP = {"id": CLIENT_OBJECT_ID, "appId": CLIENT_APP_ID, "displayName": "my-app"}
APP_LIST = {"value": [APP]}
CLIENT_SP = {"id": CLIENT_SP_ID, "appId": CLIENT_APP_ID}
SHAREPOINT_SP = {
    "id": SHAREPOINT_SP_ID,
    "appId": SHAREPOINT_APP_ID,
    "appRoles": [{"id": ROLE_ID, "value": "Sites.Selected"}],
    "appRoleAssignedTo": [],
}
GRANTED_SP = {
    **SHAREPOINT_SP,
    "appRoleAssignedTo": [{"id": ASSIGNMENT_ID, "appRoleId": ROLE_ID, "principalId": CLIENT_SP_ID}],
}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

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


def _methods(transport: _RecordingTransport) -> list[str]:
    return [request.method for request in transport.requests]


def test_application_grant_resolves_resource_by_name():
    client, transport = _client([APP_LIST, {"value": [SHAREPOINT_SP]}, CLIENT_SP, {"id": "assignment"}])
    app = client.applications.ensure("my-app").execute_query()

    app.grant_permissions("Sites.Selected", ResourceName.SharePoint).execute_query()

    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Get, HttpMethod.Get, HttpMethod.Post]
    assert "$filter=displayName eq 'Office 365 SharePoint Online'" in transport.requests[1].url


def test_service_principal_revoke_only_removes_the_requested_role():
    resource = {
        **SHAREPOINT_SP,
        "appRoles": [
            {"id": ROLE_ID, "value": "Sites.Selected"},
            {"id": OTHER_ROLE_ID, "value": "Sites.Read.All"},
        ],
        "appRoleAssignedTo": [
            {"id": "assignment-selected", "appRoleId": ROLE_ID, "principalId": CLIENT_SP_ID},
            {"id": "assignment-read", "appRoleId": OTHER_ROLE_ID, "principalId": CLIENT_SP_ID},
        ],
    }
    client, transport = _client([resource, CLIENT_SP, {"http_status": 204}])

    client.service_principals.get_by_app_id(SHAREPOINT_APP_ID).revoke_application_permissions(
        CLIENT_APP_ID, "Sites.Selected"
    ).execute_query()

    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Get, HttpMethod.Delete]
    assert transport.requests[-1].url.endswith("appRoleAssignedTo/assignment-selected")
    assert all("assignment-read" not in request.url for request in transport.requests)
