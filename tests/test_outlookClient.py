from unittest import TestCase

from client.office365.outlook.outlook_client import OutlookClient
from examples.settings import settings


class TestOutlookClient(TestCase):
    def test_get_contacts(self):
        client = OutlookClient(username=settings['username'], password=settings['password'])
        contacts = client.get_contacts()
        client.load(contacts)
        #client.execute_query()
        #self.assertIsNotNone(contacts)
