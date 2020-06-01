from unittest import TestCase
from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.list_data_service import ListDataService
from settings import settings


class TestSharePointListDataService(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSharePointListDataService, cls).setUpClass()
        credential = ClientCredential(settings['client_credentials']['client_id'],
                                      settings['client_credentials']['client_secret'])
        cls.client = ListDataService.connect_with_credentials(settings['url'], credential)

    def test1_get_list_items(self):
        items = self.client.get_list_items("Documents")
        self.client.load(items)
        self.client.execute_query()
        self.assertIsNotNone(items)
