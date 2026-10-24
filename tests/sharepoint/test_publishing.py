"""Tests for SharePoint publishing features including site pages, video service, and page management."""

from __future__ import annotations

from urllib.parse import urlparse

from office365.sharepoint.publishing.pages.service import SitePageService
from office365.sharepoint.publishing.video.service_discoverer import (
    VideoServiceDiscoverer,
)

from tests import answered_null
from tests.sharepoint.sharepoint_case import SPTestCase


class TestPublishing(SPTestCase):
    """Test SharePoint publishing features."""

    def test_01_init_site_page_service(self):
        """Initialize and verify site page service."""
        svc = self.client.site_pages.get().execute_query()
        self.assertIsNotNone(svc.resource_path)

    # def test3_get_time_zone(self):
    #    time_zone = SitePageService.get_time_zone(self.client, "Moscow").execute_query()
    #    self.assertIsInstance(time_zone, PrimaryCityTime)

    def test_02_compute_file_name(self):
        """Compute file name for a site page."""
        result = SitePageService.compute_file_name(self.client, "Test page").execute_query()
        self.assertIsNotNone(result.value)

    def test_03_file_picker_tab_options(self):
        """Retrieve file picker tab options."""
        result = SitePageService.file_picker_tab_options(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test_04_org_assets(self):
        """Retrieve organization assets.

        Organization assets are a tenant opt-in: a tenant that has not provisioned
        them answers ``OrgAssets: null`` for every site.
        """
        result = SitePageService.org_assets(self.client).execute_query()
        if answered_null(result):
            self.skipTest("The tenant has not provisioned organization assets")
        self.assertIsNotNone(result.value)

    def test_05_get_video_service_manager(self):
        """Retrieve video service manager discoverer."""
        discoverer = VideoServiceDiscoverer(self.client).get().execute_query()
        self.assertIsNotNone(discoverer.video_portal_url)

    def test_06_get_page_by_name(self):
        """Get a site page by name."""
        page = self.client.site_pages.pages.find_by_name("Home.aspx", required=True).execute_query()
        self.assertIsNotNone(page.resource_path)

    def test_07_can_create_page(self):
        """Check if a page can be created."""
        result = self.client.site_pages.can_create_page().execute_query()
        self.assertIsNotNone(result.value)

    def test_08_get_current_user_memberships(self):
        """Get current user memberships via site page service."""
        result = SitePageService.get_current_user_memberships(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test_09_get_page_diagnostics(self):
        """Get page diagnostics for the site's own home page.

        The path is server-relative to the site being tested, and diagnostics exist
        only for a page the site actually serves: a path under another site (or a
        page that has not been rendered yet) answers ``500 Unable to get Page
        Diagnostics results at this time``.
        """
        page_path = f"{urlparse(self.client.base_url).path}/SitePages/Home.aspx"
        result = self.client.page_diagnostics.by_page(page_path).execute_query()
        self.assertIsNotNone(result.value)

    def test_10_checkout_page(self):
        """Check out a site page."""
        page = self.client.site_pages.pages.find_by_name("Home.aspx", required=True)
        page.checkout_page().execute_query()
        self.assertIsNotNone(page.resource_path)
        self.assertTrue(page.is_page_checked_out_to_current_user)

    def test_11_list_checkout_pages(self):
        """List checked-out files from the Site Pages library."""
        pages_list = self.client.web.lists.get_by_title("Site Pages")
        result = pages_list.get_checked_out_files().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_12_discard_page(self):
        """Discard check-out on a site page."""
        page = self.client.site_pages.pages.find_by_name("Home.aspx", required=True)
        page.discard_page().execute_query()
        self.assertFalse(
            page.is_page_checked_out_to_current_user,
            "Page is expected to be checked in",
        )

    # def test15_share_page_preview_by_email(self):
    #    page = self.client.site_pages.pages.get_by_url("/sites/team/SitePages/Home.aspx")
    #    page.share_page_preview_by_email("This page has been shared with you",
    #                                     [test_user_principal_name_alt]).execute_query()
