from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url


class TestAdmin(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = ClientContext(test_admin_site_url).with_credentials(
            test_admin_credentials
        )

    def test1_get(self):
        from office365.sharepoint.administration.analytics.usage_service import (
            SPAnalyticsUsageService,
        )

        analytics = SPAnalyticsUsageService(self.client).get().execute_query()
        self.assertIsNotNone(analytics.resource_path)
