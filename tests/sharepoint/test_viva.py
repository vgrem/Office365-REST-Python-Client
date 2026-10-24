"""Tests for SharePoint Viva Engage features including app configuration and dashboard content."""

from __future__ import annotations

from office365.runtime.client_request_exception import ClientRequestException

from tests.sharepoint.sharepoint_case import SPTestCase


class TestViva(SPTestCase):
    """Test SharePoint Viva features."""

    def test_01_get_app_configuration(self):
        """Get the app configuration.

        The Viva Engage app configuration is only served for a home site; any other
        web is refused by the service.
        """
        try:
            return_type = self.client.ee.app_configuration.get().execute_query()
        except ClientRequestException as e:
            self.skipTest(f"The web is not a home site: {e}")
        self.assertIsNotNone(return_type.resource_path)

    # def test2_get_viva_home(self):
    #    return_type = self.client.ee.viva_home().execute_query()
    #    self.assertIsNotNone(return_type.resource_path)

    def test_02_get_dashboard_content(self):
        """Get dashboard content."""
        return_type = self.client.ee.dashboard_content().execute_query()
        self.assertIsNotNone(return_type.value)

    def test_03_get_full_dashboard_content(self):
        """Get full dashboard content."""
        return_type = self.client.ee.full_dashboard_content().execute_query()
        self.assertIsNotNone(return_type.value)

    # def test5_get_working_set_files(self):
    #   from office365.sharepoint.copilot.file_collection import CopilotFileCollection
    #   return_type = CopilotFileCollection.get_working_set_files(self.client, 10).execute_query()
    #   self.assertIsNotNone(return_type.resource_path)
