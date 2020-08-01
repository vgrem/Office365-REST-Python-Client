from unittest import TestCase

from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.listdatasvc.list_data_service import ListDataService


class TestSharePointListDataService(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSharePointListDataService, cls).setUpClass()
        credential = ClientCredential(settings['client_credentials']['client_id'],
                                      settings['client_credentials']['client_secret'])
        cls.client = ListDataService.connect_with_credentials(settings['url'], credential)

    def test1_get_list_items(self):
        pass
