from __future__ import annotations

from datetime import datetime, timezone

from office365.sharepoint.webhooks.subscription_information import SubscriptionInformation


def test_subscription_information_expiration_is_utc_z():
    info = SubscriptionInformation(
        notificationUrl="https://example.com/hook",
        resource="resource",
        expirationDateTime=datetime(2026, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc),
    )
    assert info.to_json()["expirationDateTime"] == "2026-01-01T12:00:00Z"


def _graph_client():
    from office365.graph_client import GraphClient

    return GraphClient(tenant="contoso.onmicrosoft.com")


def test_graph_subscription_add_accepts_resource_path():
    from office365.runtime.paths.resource_path import ResourcePath

    client = _graph_client()
    client.subscriptions.add(
        change_type="updated",
        notification_url="https://example.com/hook",
        resource=ResourcePath("me/drive/root"),
        expiration=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )
    assert client._queries[-1]._parameters_type["resource"] == "me/drive/root"
