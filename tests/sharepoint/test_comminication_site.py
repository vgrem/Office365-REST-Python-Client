"""Tests for SharePoint communication site creation, management, and hub registration."""

from __future__ import annotations

import uuid
from typing import ClassVar, Optional

from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.tenant import Tenant

from tests import (
    test_admin_site_url,
    test_client_id,
    test_password,
    test_root_site_url,
    test_tenant,
    test_username,
)
from tests.sharepoint.sharepoint_case import SPTestCase


class TestCommunicationSite(SPTestCase):
    """Tests for SharePoint communication site lifecycle operations."""

    target_site: ClassVar[Optional[Site]] = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ctx = ClientContext(test_root_site_url).with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )
        cls.client = ctx

    def test_01_create_site(self):
        """Create a new communication site."""
        site_alias = f"site{uuid.uuid4().hex}"
        comm_site = self.client.create_communication_site(site_alias, site_alias).execute_query()
        self.assertIsNotNone(comm_site.resource_path)
        TestCommunicationSite.target_site = comm_site

    def test_02_is_comm_site(self):
        """Verify the site is a communication site."""
        target = TestCommunicationSite.target_site
        if not target:
            self.skipTest("No resource from previous test")
        result = target.is_comm_site().execute_query()
        self.assertIsNotNone(result.value)

    def test_03_set_as_home_site(self):
        """Set the communication site as the home site.

        A tenant has exactly one home site, a tenant-wide setting that this suite
        only borrows: when the tenant already designates one, the service answers
        ``Value cannot be null. Parameter name: requestUrl`` instead of replacing it.
        """
        target = TestCommunicationSite.target_site
        if not target:
            self.skipTest("No resource from previous test")
        try:
            result = target.set_as_home_site().execute_query()
        except ClientRequestException as e:
            self.skipTest(f"The tenant does not hand its home site to this site: {e}")
        self.assertIsNotNone(result.value)

    def test_04_is_valid_home_site(self):
        """Verify the site is a valid home site."""
        target = TestCommunicationSite.target_site
        if not target:
            self.skipTest("No resource from previous test")
        result = target.is_valid_home_site().execute_query()
        self.assertIsNotNone(result.value)

    # def test5_get_home_details(self):
    #    result = self.client.home_site.details().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_05_register_hub_site(self):
        """Register the site as a hub site."""
        target = TestCommunicationSite.target_site
        if not target:
            self.skipTest("No resource from previous test")
        self.assertIsNotNone(target.url)
        tenant = Tenant.from_url(test_admin_site_url).with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )
        props = tenant.register_hub_site(target.url).execute_query()
        self.assertIsNotNone(props.site_id)
        site = target.get().execute_query()
        self.assertTrue(site.is_hub_site)

    def test_06_unregister_hub_site(self):
        """Unregister the site as a hub site."""
        target = TestCommunicationSite.target_site
        if not target:
            self.skipTest("No resource from previous test")
        self.assertIsNotNone(target.url)
        client_admin = ClientContext(test_admin_site_url).with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )
        tenant = Tenant(client_admin)
        tenant.unregister_hub_site(target.url).execute_query()

    def test_07_delete_site(self):
        """Delete the communication site."""
        target = TestCommunicationSite.target_site
        if not target:
            self.skipTest("No resource from previous test")
        target.delete_object().execute_query()
