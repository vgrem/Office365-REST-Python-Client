"""Offline tests for ``Site.grant_access`` / ``Site.revoke_access`` and their app-aware twins.

Covers the request shape of the site-permission convenience wrappers: the
``POST /sites/{id}/permissions`` body for entity and object-ID identities, role
normalisation, the identity-matched deletes issued by ``revoke_access``, and the
application (client) ID / ``Application`` entity forms that resolve the service
principal internally.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from tests._scripted_transport import RoutingTransport

SITE_ID = "contoso.sharepoint.com,site-guid,web-guid"
APP_ID = "11111111-1111-1111-1111-111111111111"
SP_OBJECT_ID = "22222222-2222-2222-2222-222222222222"
APPLICATION_OBJECT_ID = "33333333-3333-3333-3333-333333333333"


def _client(transport: RoutingTransport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def _site(client: GraphClient):
    return client.sites[SITE_ID]


def test_revoke_access_deletes_only_matching_permissions():
    payload = {
        "value": [
            {"id": "perm-1", "roles": ["write"], "grantedToIdentitiesV2": [{"application": {"id": APP_ID}}]},
            {"id": "perm-2", "roles": ["read"], "grantedToIdentitiesV2": [{"application": {"id": "someone-else"}}]},
            {"id": "perm-3", "roles": ["owner"], "grantedToV2": {"application": {"id": APP_ID}}},
        ]
    }
    transport = RoutingTransport([("permissions", payload)])
    client = _client(transport)

    _site(client).revoke_access(APP_ID).execute_query()

    deletes = [r.url.rsplit("/", 1)[-1] for r in transport.requests if r.method == HttpMethod.Delete]
    assert deletes == ["perm-1", "perm-3"]


def test_revoke_app_access_resolves_service_principal_and_deletes():
    payload = {
        "value": [
            {"id": "perm-1", "roles": ["write"], "grantedToIdentitiesV2": [{"application": {"id": SP_OBJECT_ID}}]},
            {"id": "perm-2", "roles": ["read"], "grantedToIdentitiesV2": [{"application": {"id": "someone-else"}}]},
        ]
    }
    transport = RoutingTransport(
        [
            ("servicePrincipals", {"id": SP_OBJECT_ID, "displayName": "Contoso App"}),
            ("permissions", payload),
        ]
    )
    client = _client(transport)

    _site(client).revoke_app_access(APP_ID).execute_query()

    deletes = [r.url.rsplit("/", 1)[-1] for r in transport.requests if r.method == HttpMethod.Delete]
    assert deletes == ["perm-1"]
