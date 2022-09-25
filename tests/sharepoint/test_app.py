from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.marketplace.sitecollection.appcatalog.accessor import SiteCollectionCorporateCatalogAccessor
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.settings import TenantSettings
from tests import test_user_credentials, test_admin_site_url
from tests.sharepoint.sharepoint_case import SPTestCase


class TestApp(SPTestCase):
    catalog = None  # type:  SiteCollectionCorporateCatalogAccessor

    def test_1_get_app_catalog(self):
        admin_client = ClientContext(test_admin_site_url).with_credentials(test_user_credentials)
        tenant_settings = TenantSettings.current(admin_client).get().execute_query()
        self.assertIsNotNone(tenant_settings.resource_path)
        site = Site.from_url(tenant_settings.corporate_catalog_url).with_credentials(test_user_credentials)
        catalog = site.root_web.site_collection_app_catalog.get().execute_query()
        self.assertIsNotNone(catalog.resource_path)
        self.__class__.catalog = catalog

    #def test_2_list_apps(self):
    #    apps = self.__class__.catalog.available_apps.get().execute_query()
    #    self.assertIsNotNone(apps.resource_path)

