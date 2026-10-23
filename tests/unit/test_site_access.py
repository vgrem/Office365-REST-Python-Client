"""Offline tests for ``Site.grant_access`` / ``Site.revoke_access`` and their app-aware twins.

Covers the request shape of the site-permission convenience wrappers: the
``POST /sites/{id}/permissions`` body for entity and object-ID identities, role
normalisation, the identity-matched deletes issued by ``revoke_access``, and the
application (client) ID / ``Application`` entity forms that resolve the service
principal internally.
"""

from __future__ import annotations

import pytest
from office365.directory.applications.application import Application
from office365.directory.serviceprincipals.service_principal import ServicePrincipal
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


def _service_principal(client: GraphClient) -> ServicePrincipal:
    sp = ServicePrincipal(client)
    sp.set_property("id", APP_ID)
    sp.set_property("displayName", "Contoso App")
    return sp


def test_grant_access_with_entity_posts_application_identity():
    transport = RoutingTransport([("permissions", {})])
    client = _client(transport)

    _site(client).grant_access(_service_principal(client), "write").execute_query()

    request = transport.requests[-1]
    assert request.method == HttpMethod.Post
    assert request.url.endswith(f"/sites/{SITE_ID}/permissions")
    assert request.data["roles"] == ["write"]  # a bare role is normalised to a list
    grantee = request.data["grantedToIdentities"][0]["application"]
    assert grantee["id"] == APP_ID
    assert grantee["displayName"] == "Contoso App"


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


def test_app_access_without_app_id_raises():
    client = _client(RoutingTransport([("permissions", {})]))
    app = Application(client)

    with pytest.raises(ValueError, match="application"):
        _site(client).grant_app_access(app, "write")
