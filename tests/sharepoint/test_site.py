"""Tests for SharePoint site operations including creation, status, deletion, and site properties."""

from __future__ import annotations

import uuid
from typing import ClassVar, Optional

from office365.runtime.exceptions import AccessDeniedException
from office365.sharepoint.lists.templates.type import ListTemplateType
from office365.sharepoint.portal.sites.creation_response import SPSiteCreationResponse
from office365.sharepoint.portal.sites.status import SiteStatus
from office365.sharepoint.sites.site import Site

from tests import (
    test_admin_credentials,
    test_client_id,
    test_site_url,
    test_tenant,
    test_user_principal_name_alt,
)
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSite(SPTestCase):
    """Test SharePoint site operations."""

    site_response: ClassVar[Optional[SPSiteCreationResponse]] = None

    def test_01_if_site_loaded(self):
        """Verify that the site resource was loaded."""
        site = self.client.site.get().execute_query()
        self.assertIs(site.is_property_available("Url"), True, "Site resource was not requested")
        self.assertIs(site.is_property_available("RootWeb"), False)

    def test_02_if_site_exists(self):
        """Check if a site exists at the current URL."""
        site_url = self.client.site.url
        self.assertIsNotNone(site_url)
        result = Site.exists(self.client, site_url).execute_query()
        self.assertIsNotNone(result.value)

    def test_03_get_site_by_id(self):
        """Get site URL by site ID."""
        site_id = self.client.site.id
        self.assertIsNotNone(site_id)
        result = Site.get_url_by_id(self.client, site_id).execute_query()
        self.assertIsNotNone(result.value)

    def test_04_check_is_deletable(self):
        """Check if the current site is deletable."""
        result = self.client.site.check_is_deletable().execute_query()
        self.assertIsNotNone(result.value)

    def test_05_get_site_catalog(self):
        """Get the site catalog for AppDataCatalog."""
        result = self.client.site.get_catalog(ListTemplateType.AppDataCatalog).get().execute_query()
        self.assertIsNotNone(result.title)

    def test_06_get_web_templates(self):
        """Get available web templates for the site."""
        result = self.client.site.get_web_templates().execute_query()
        self.assertIsNotNone(result)

    def test_07_get_site_logo(self):
        """Get the site logo."""
        result = self.client.site.get_site_logo().execute_query()
        self.assertIsNotNone(result.value)

    def test_08_open_web_by_id(self):
        """Open a child web by its ID."""
        web = self.client.web.get().execute_query()
        self.assertIsNotNone(web.id)
        child_web = self.client.site.open_web_by_id(web.id).execute_query()
        self.assertIsNotNone(child_web.id)

    # def test_10_get_site_links(self):
    #    result = self.client.site_linking_manager.get_site_links().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_09_create_site(self):
        """Create a new communication site."""
        site_url = f"{test_site_url}/sites/{uuid.uuid4().hex}"
        result = self.client.site_manager.create("Comm Site", site_url, test_user_principal_name_alt).execute_query()
        self.assertIsNotNone(result.value)
        TestSite.site_response = result.value

    def test_10_get_site_status(self):
        """Get the status of the newly created site."""
        site_response = TestSite.site_response
        if not site_response:
            self.skipTest("No site response from previous test")
        site_url = site_response.SiteUrl
        self.assertIsNotNone(site_url)
        result = self.client.site_manager.get_status(site_url).execute_query()
        self.assertIsNotNone(result.value.SiteStatus)
        self.assertTrue(result.value.SiteStatus != SiteStatus.Error)

    def test_11_get_site_url(self):
        """Get the site URL by site ID."""
        site_response = TestSite.site_response
        if not site_response:
            self.skipTest("No site response from previous test")
        site_id = site_response.SiteId
        self.assertIsNotNone(site_id)
        result = self.client.site_manager.get_site_url(site_id).execute_query()
        self.assertIsNotNone(result.value)
        self.assertEqual(site_response.SiteUrl, result.value)

    def test_12_is_deletable(self):
        """Check if the current site is deletable (alternate method)."""
        result = self.client.site.is_deletable().execute_query()
        self.assertIsNotNone(result.value)

    def test_13_delete_site(self):
        """Delete the created communication site.

        Deleting a site collection is a tenant-administrator operation: unless the
        configured test account is a SharePoint administrator the service answers
        403, and the site created earlier stays behind.
        """
        site_response = TestSite.site_response
        if not site_response:
            self.skipTest("No site response from previous test")
        from office365.sharepoint.client_context import ClientContext

        admin_ctx = ClientContext(self.client.base_url).with_username_and_password(
            test_tenant, test_client_id, test_admin_credentials.userName, test_admin_credentials.password
        )
        site_id = site_response.SiteId
        self.assertIsNotNone(site_id)
        try:
            admin_ctx.site_manager.delete(site_id).execute_query()
        except AccessDeniedException:
            self.skipTest(
                f"{test_admin_credentials.userName} is not a SharePoint administrator; "
                f"site {site_response.SiteUrl} was left in place"
            )

    # def test_16_get_block_download_policy_for_files_data(self):
    #    result = self.client.site.get_block_download_policy_for_files_data().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_14_site_font_packages(self):
        """Get site font packages."""
        result = self.client.site_font_packages.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test_18_get_block_download_policy_for_files_data(self):
    #    result = self.client.site.get_block_download_policy_for_files_data().execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_19_get_top_files(self):
    #    result = self.client.site_manager_svc.top_files().execute_query()
    #    self.assertIsNotNone(result.value)
