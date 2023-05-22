from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.marketplace.sitecollection.appcatalog.accessor import SiteCollectionCorporateCatalogAccessor
from tests import test_admin_site_url, test_admin_credentials
from tests.sharepoint.sharepoint_case import SPTestCase


class TestApp(SPTestCase):
    catalog = None  # type:  SiteCollectionCorporateCatalogAccessor
    admin_client = None  # type:  ClientContext

    def test_1_get_app_catalog(self):
        admin_client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
        site = admin_client.tenant.get_corporate_catalog_site().execute_query()
        catalog = site.root_web.site_collection_app_catalog.get().execute_query()
        self.assertIsNotNone(catalog.resource_path)
        self.__class__.catalog = catalog
        self.__class__.admin_client = admin_client


    #def test_2_list_apps(self):
    #    apps = self.__class__.catalog.available_apps.get().execute_query()
    #    self.assertIsNotNone(apps.resource_path)

    #def test_3_available_addins(self):
    #    result = self.__class__.admin_client.web.available_addins([test_site_url]).execute_query()
    #    self.assertIsNotNone(result.value)
