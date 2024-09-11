from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url
from tests.sharepoint.sharepoint_case import SPTestCase


class TestBdc(SPTestCase):
    app_site_url = None

    def test_1_get_corporate_catalog_url(self):
        admin_client = ClientContext(test_admin_site_url).with_credentials(
            test_admin_credentials
        )
        return_type = admin_client.tenant_settings.get().execute_query()
        self.assertIsNotNone(return_type.corporate_catalog_url)
        self.__class__.app_site_url = return_type.corporate_catalog_url

    # def test_2_get_app_bdc_catalog(self):
    #    client = ClientContext(self.app_site_url).with_credentials(
    #        test_user_credentials
    #    )
    #    result = client.web.get_app_bdc_catalog().execute_query()
    #    self.assertIsNotNone(result.resource_path)
