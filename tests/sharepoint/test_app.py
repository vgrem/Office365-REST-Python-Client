"""Tests for SharePoint app catalog operations (tenant app catalog, site collection app catalog)."""

from __future__ import annotations

import os
from typing import ClassVar, Optional

from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.marketplace.app_metadata import CorporateCatalogAppMetadata
from office365.sharepoint.marketplace.tenant.appcatalog.accessor import (
    TenantCorporateCatalogAccessor,
)

from tests import (
    test_admin_site_url,
    test_client_id,
    test_password,
    test_team_site_url,
    test_tenant,
    test_username,
)
from tests.sharepoint.sharepoint_case import SPTestCase


class TestApp(SPTestCase):
    """Tests for SharePoint app catalog lifecycle operations."""

    app: ClassVar[Optional[CorporateCatalogAppMetadata]] = None
    site_col_app_catalog: ClassVar[Optional[TenantCorporateCatalogAccessor]] = None

    @classmethod
    def setUpClass(cls):
        cls.admin_client: ClientContext = ClientContext(test_admin_site_url).with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )
        cls.tenant_app_catalog: TenantCorporateCatalogAccessor = cls.admin_client.web.tenant_app_catalog

    def test_01_load_tenant_app_catalog(self):
        """Load the tenant app catalog."""
        result = self.tenant_app_catalog.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_02_get_corporate_catalog_site(self):
        """Get the corporate catalog site URL."""
        site = self.admin_client.tenant.get_corporate_catalog_site().execute_query()
        self.assertIsNotNone(site.resource_path)

    def test_03_add_app(self):
        """Add an app package to the tenant app catalog."""
        app_path = f"{os.path.dirname(__file__)}/../data/react-banner.sppkg"
        app_file = self.tenant_app_catalog.app_from_path(app_path, True).execute_query()
        self.assertIsNotNone(app_file.resource_path)

    def test_04_list_apps(self):
        """List available apps in the tenant app catalog."""
        apps = self.tenant_app_catalog.available_apps.get().execute_query()
        self.assertIsNotNone(apps.resource_path)

    def test_05_get_app(self):
        """Get a specific app from the tenant app catalog."""
        target = TestApp.app
        if not target:
            self.skipTest("No resource from previous test")
        app = self.tenant_app_catalog.available_apps.get_by_title("Starter Kit - Banner").execute_query()
        self.assertIsNotNone(app.resource_path)
        TestApp.app = app

    def test_06_list_site_collection_app_catalogs_sites(self):
        """List site collection app catalog sites."""
        sites = self.tenant_app_catalog.site_collection_app_catalogs_sites.get().execute_query()
        self.assertIsNotNone(sites.resource_path)

    def test_07_get_site_collection_app_catalog(self):
        """Get the site collection app catalog for a team site."""
        site_client = ClientContext(test_team_site_url).with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )
        result = site_client.web.site_collection_app_catalog.get().execute_query()
        self.assertIsNotNone(result.resource_path)
        # type(self).site_col_app_catalog = result

    # def test6_available_addins(self):
    #    result = self.admin_client.web.available_addins([test_team_site_url]).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test7_create_credential_field(self):
    #    name = create_unique_name("cred field ")
    #    result = TargetApplicationField.create(self.admin_client, name, False, 1).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test8_list_app_requests(self):
    #    result = self.app_catalog.app_requests().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_08_get_addin_principals_having_permissions_in_sites(self):
        """Get add-in principals having permissions in specified sites."""
        try:
            result = self.admin_client.web.get_addin_principals_having_permissions_in_sites(
                urls=[test_team_site_url]
            ).execute_query()
        except ClientRequestException as e:
            self.skipTest(f"The signed-in identity may not enumerate add-in principals: {e}")
        self.assertIsNotNone(result.value)
