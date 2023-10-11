from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url


class TestApp(TestCase):
    catalog = None  # type:  TenantCorporateCatalogAccessor
    admin_client = None  # type:  ClientContext

    @classmethod
    def setUpClass(cls):
        cls.admin_client = ClientContext(test_admin_site_url).with_credentials(
            test_admin_credentials
        )
        cls.catalog = cls.admin_client.web.tenant_app_catalog

    def test_1_load_tenant_app_catalog(self):
        result = self.catalog.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_2_get_corporate_catalog_site(self):
        site = self.admin_client.tenant.get_corporate_catalog_site()
        self.assertIsNotNone(site.resource_path)

    def test_3_list_apps(self):
        apps = self.__class__.catalog.available_apps.get().execute_query()
        self.assertIsNotNone(apps.resource_path)

    # def test_4_is_app_upgrade_available(self):
    #    apps = self.catalog.available_apps.top(1).get().execute_query()
    #    self.assertEqual(len(apps), 1)
    #    result = self.catalog.is_app_upgrade_available(apps[0].id).execute_query()
    #    self.assertIsNotNone(result.value)

    def test_5_list_site_collection_app_catalogs_sites(self):
        sites = self.catalog.site_collection_app_catalogs_sites.get().execute_query()
        self.assertIsNotNone(sites.resource_path)

    # def test_6_available_addins(self):
    #    result = self.__class__.admin_client.web.available_addins([test_team_site_url]).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_7_create_credential_field(self):
    #    name = create_unique_name("cred field ")
    #    result = TargetApplicationField.create(self.admin_client, name, False, 1).execute_query()
    #    self.assertIsNotNone(result.value)
