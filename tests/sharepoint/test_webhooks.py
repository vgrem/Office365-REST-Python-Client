"""Tests for SharePoint webhook subscriptions including creation, listing, update, and deletion."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import ClassVar, Optional

from office365.sharepoint.lists.list import List
from office365.sharepoint.webhooks.subscription import Subscription

from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPWebHooks(SPTestCase):
    """Test SharePoint webhook subscriptions."""

    target_list: ClassVar[Optional[List]] = None
    target_subscription: ClassVar[Optional[Subscription]] = None
    push_service_url = "https://westeurope0.pushnp.svc.ms/notifications?token=526a9d28-d4ec-45b7-81b9-4e1599524784"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.target_list = cls.client.web.lists.get_by_title("Documents")

    @classmethod
    def tearDownClass(cls):
        pass

    def test_01_create_subscription(self):
        """Create a new webhook subscription."""
        target_list = TestSPWebHooks.target_list
        if not target_list:
            self.skipTest("No target list from setup")
        expiration = datetime.now(timezone.utc) + timedelta(days=30)
        subscription = target_list.subscriptions.add(self.push_service_url, expiration).execute_query()
        self.assertIsNotNone(subscription.notification_url)
        TestSPWebHooks.target_subscription = subscription

    def test_02_list_webhooks(self):
        """List all webhook subscriptions on the target list."""
        target_list = TestSPWebHooks.target_list
        if not target_list:
            self.skipTest("No target list from setup")
        subscriptions = target_list.subscriptions.get().execute_query()
        self.assertGreater(len(subscriptions), 0)

    def test_03_update_subscription(self):
        """Update the expiration date of a webhook subscription."""
        target_subscription = TestSPWebHooks.target_subscription
        if not target_subscription:
            self.skipTest("No target subscription from previous test")
        subscription = target_subscription
        subscription.expiration_datetime = datetime.now(timezone.utc) + timedelta(days=10)
        subscription.update().execute_query()

    def test_04_delete_subscription(self):
        """Delete the webhook subscription."""
        target_subscription = TestSPWebHooks.target_subscription
        if not target_subscription:
            self.skipTest("No target subscription from previous test")
        subscription = target_subscription
        subscription.delete_object().execute_query()
