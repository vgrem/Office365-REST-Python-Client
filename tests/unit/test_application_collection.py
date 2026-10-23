"""Offline tests for the ``applications.ensure`` / ``service_principals.ensure`` setup helpers.

Covers the get-by-display-name-or-create semantics of
``ApplicationCollection.ensure`` (and the explicit
``service_principals.ensure`` follow-up), the get-or-create behaviour of
``ServicePrincipalCollection.ensure``, and the Entra ``Request_ResourceNotFound``
classification the latter relies on.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from tests._scripted_transport import ScriptedTransport

APP_ID = "11111111-1111-1111-1111-111111111111"
APP_OBJECT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
SP_OBJECT_ID = "22222222-2222-2222-2222-222222222222"

_NOT_FOUND = {
    "http_status": 404,
    "body": {
        "error": {
            "code": "Request_ResourceNotFound",
            "message": "Resource does not exist.",
        }
    },
}

_APP = {"id": APP_OBJECT_ID, "appId": APP_ID, "displayName": "my-app"}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _client(transport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def _methods(transport: _RecordingTransport) -> list[str]:
    return [request.method for request in transport.requests]


def test_ensure_reuses_app_by_name():
    transport = _RecordingTransport([{"value": [_APP]}])
    client = _client(transport)

    app = client.applications.ensure("my-app").execute_query()

    assert app.app_id == APP_ID
    assert _methods(transport) == [HttpMethod.Get]
    assert "displayName eq 'my-app'" in transport.requests[0].url


def test_ensure_creates_app_when_missing():
    transport = _RecordingTransport([{"value": []}, _APP])
    client = _client(transport)

    app = client.applications.ensure("my-app").execute_query()

    assert app.app_id == APP_ID
    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Post]
    assert transport.requests[-1].url.endswith("/applications")
    assert transport.requests[-1].data["displayName"] == "my-app"
    assert transport.requests[-1].data["signInAudience"] == "AzureADMyOrg"


def test_ensure_app_then_service_principal_provisions_both():
    transport = _RecordingTransport(
        [
            {"value": [_APP]},  # GET applications?$filter=displayName...
            _NOT_FOUND,  # GET servicePrincipals(appId=...) -> missing
            {"id": SP_OBJECT_ID, "appId": APP_ID},  # POST servicePrincipals
        ]
    )
    client = _client(transport)

    app = client.applications.ensure("my-app").execute_query()
    sp = client.service_principals.ensure(app.app_id).execute_query()

    assert app.app_id == APP_ID
    assert sp.id == SP_OBJECT_ID
    assert _methods(transport) == [HttpMethod.Get, HttpMethod.Get, HttpMethod.Post]
    assert transport.requests[-1].url.endswith("/servicePrincipals")
    assert transport.requests[-1].data["appId"] == APP_ID


def test_service_principal_ensure_reuses_existing():
    transport = _RecordingTransport([{"id": SP_OBJECT_ID, "appId": APP_ID}])
    client = _client(transport)

    sp = client.service_principals.ensure(APP_ID).execute_query()

    assert sp.id == SP_OBJECT_ID
    assert _methods(transport) == [HttpMethod.Get]
