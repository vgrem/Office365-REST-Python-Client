from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_credentials, test_admin_site_url


class TestAdmin(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = ClientContext(test_admin_site_url).with_credentials(
            test_admin_credentials
        )
        cls.tenant = Tenant(cls.client)

    def test1_get_analytics_usage(self):
        from office365.sharepoint.administration.analytics.usage_service import (
            SPAnalyticsUsageService,
        )

        analytics = SPAnalyticsUsageService(self.client).get().execute_query()
        self.assertIsNotNone(analytics.resource_path)

    # def test2_render_policy_report(self):
    #    result = self.tenant.render_policy_report().execute_query()
    #    self.assertIsNotNone(result.value)

    # def test3_render_recent_admin_actions(self):
    #    result = self.tenant.render_recent_admin_actions().execute_query()
    #    self.assertIsNotNone(result.value)

    def test4_set_file_version_policy(self):
        result = self.tenant.set_file_version_policy(True, 100, 10).execute_query()
        self.assertIsNotNone(result.resource_path)

    def test5_get_file_version_policy(self):
        result = self.tenant.get_file_version_policy().execute_query()
        self.assertIsNotNone(result.value)

    def test6_clear_file_version_policy(self):
        result = self.tenant.clear_file_version_policy().execute_query()
        self.assertIsNotNone(result.resource_path)

    # requires SharePoint Advanced Management license
    # def test7_get_ransomware_activities(self):
    #    result = self.tenant.get_ransomware_activities().execute_query()
    #    self.assertIsNotNone(result.value)

    def test8_get_root_site_url(self):
        result = self.tenant.get_root_site_url().execute_query()
        self.assertIsNotNone(result.value)

    # def test9_get_app_service_principal(self):
    #    result = self.tenant.app_service_principal.get().execute_query()
    #    self.assertIsNotNone(result.resource_path)
