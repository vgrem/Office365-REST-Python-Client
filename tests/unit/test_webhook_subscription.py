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
