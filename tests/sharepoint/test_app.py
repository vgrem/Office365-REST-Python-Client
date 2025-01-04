from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.marketplace.app_metadata import CorporateCatalogAppMetadata
from office365.sharepoint.marketplace.tenant.appcatalog.accessor import (
    TenantCorporateCatalogAccessor,
)
from tests import test_admin_credentials, test_admin_site_url, test_team_site_url


class TestApp(TestCase):
    tenant_app_catalog = None  # type:  TenantCorporateCatalogAccessor
    admin_client = None  # type:  ClientContext
    app = None  # type:  CorporateCatalogAppMetadata
    site_col_app_catalog = None  # type:  TenantCorporateCatalogAccessor

    @classmethod
    def setUpClass(cls):
        cls.admin_client = ClientContext(test_admin_site_url).with_credentials(
            test_admin_credentials
        )
        cls.tenant_app_catalog = cls.admin_client.web.tenant_app_catalog

    def test_1_load_tenant_app_catalog(self):
        result = self.tenant_app_catalog.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_2_get_corporate_catalog_site(self):
        site = self.admin_client.tenant.get_corporate_catalog_site().execute_query()
        self.assertIsNotNone(site.resource_path)

    def test_3_add_app(self):
        app_path = "../../examples/sharepoint/alm/react-banner.sppkg"
        app_file = self.__class__.tenant_app_catalog.app_from_path(
            app_path, True
        ).execute_query()
        self.assertIsNotNone(app_file.resource_path)

    def test_4_list_apps(self):
        apps = self.__class__.tenant_app_catalog.available_apps.get().execute_query()
        self.assertIsNotNone(apps.resource_path)

    def test_5_get_app(self):
        app = self.__class__.tenant_app_catalog.available_apps.get_by_title(
            "Starter Kit - Banner"
        ).execute_query()
        self.assertIsNotNone(app.resource_path)
        self.__class__.app = app

    # def test_6_remove_app(self):
    #    self.__class__.app.remove().execute_query()

    def test_5_list_site_collection_app_catalogs_sites(self):
        sites = (
            self.tenant_app_catalog.site_collection_app_catalogs_sites.get().execute_query()
        )
        self.assertIsNotNone(sites.resource_path)

    def test_6_get_site_collection_app_catalog(self):
        site_client = ClientContext(test_team_site_url).with_credentials(
            test_admin_credentials
        )
        result = site_client.web.site_collection_app_catalog.get().execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.site_col_app_catalog = result

    # def test_6_available_addins(self):
    #    result = self.__class__.admin_client.web.available_addins([test_team_site_url]).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_7_create_credential_field(self):
    #    name = create_unique_name("cred field ")
    #    result = TargetApplicationField.create(self.admin_client, name, False, 1).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_8_list_app_requests(self):
    #    result = self.__class__.app_catalog.app_requests().execute_query()
    #    self.assertIsNotNone(result.value)
