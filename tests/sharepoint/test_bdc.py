from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url


class TestBdc(TestCase):
    def test_1_get_corporate_catalog_url(self):
        client = ClientContext(test_admin_site_url).with_credentials(
            test_admin_credentials
        )
        return_type = client.tenant_settings.get().execute_query()
        self.assertIsNotNone(return_type.corporate_catalog_url)
