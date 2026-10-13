from __future__ import annotations

from datetime import datetime, timezone

from office365.sharepoint.webhooks.subscription import Subscription
from office365.sharepoint.webhooks.subscription_information import SubscriptionInformation


class _FakeContext:
    pass


def test_subscription_information_expiration_is_utc_z():
    info = SubscriptionInformation(
        notificationUrl="https://example.com/hook",
        resource="resource",
        expirationDateTime=datetime(2026, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc),
    )
    assert info.to_json()["expirationDateTime"] == "2026-01-01T12:00:00Z"


def test_subscription_expiration_setter_is_utc_z():
    subscription = Subscription(_FakeContext())
    subscription.expiration_datetime = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert subscription.properties["expirationDateTime"] == "2026-01-01T12:00:00Z"


def test_subscription_expiration_setter_keeps_strings():
    subscription = Subscription(_FakeContext())
    subscription.expiration_datetime = "2026-01-01T12:00:00Z"
    assert subscription.properties["expirationDateTime"] == "2026-01-01T12:00:00Z"


def _graph_client():
    from office365.graph_client import GraphClient

    return GraphClient(tenant="contoso.onmicrosoft.com")


def test_graph_subscription_add_payload_uses_utc_z():
    client = _graph_client()
    client.subscriptions.add(
        change_type="updated",
        notification_url="https://example.com/hook",
        resource="/users",
        expiration=datetime(2026, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc),
        client_state="secret",
    )
    payload = client._queries[-1]._parameters_type
    assert payload["changeType"] == "updated"
    assert payload["notificationUrl"] == "https://example.com/hook"
    assert payload["resource"] == "users"
    assert payload["expirationDateTime"] == "2026-01-01T12:00:00Z"
    assert payload["clientState"] == "secret"


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


def test_graph_subscription_expiration_setter_serialises_utc_z():
    client = _graph_client()
    subscription = client.subscriptions.add(
        change_type="updated",
        notification_url="https://example.com/hook",
        resource="users",
        expiration=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )
    subscription.expiration_datetime = datetime(2027, 2, 2, 9, 0, 0, tzinfo=timezone.utc)
    assert subscription.to_json()["expirationDateTime"] == "2027-02-02T09:00:00Z"


def test_graph_subscription_expiration_setter_accepts_string():
    client = _graph_client()
    subscription = client.subscriptions.add(
        change_type="updated",
        notification_url="https://example.com/hook",
        resource="users",
        expiration=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )
    subscription.expiration_datetime = "2028-03-03T10:00:00+00:00"
    assert subscription.to_json()["expirationDateTime"] == "2028-03-03T10:00:00Z"
