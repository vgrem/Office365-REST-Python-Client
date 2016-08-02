from unittest import TestCase

from client.office365.outlook.outlook_client import OutlookClient
from examples.settings import settings


class TestOutlookClient(TestCase):
    def test_create_contacts(self):
        client = OutlookClient(username=settings['username'], password=settings['password'])

        contact_info = {
            "GivenName": "Pavel",
            "Surname": "Bansky",
            "EmailAddresses": [
                {
                    "Address": "pavelb@a830edad9050849NDA1.onmicrosoft.com",
                    "Name": "Pavel Bansky"
                }
            ],
            "BusinessPhones": [
                "+1 732 555 0102"
            ]
        }

        contact = client.get_contacts().add(contact_info)
        client.execute_query()
        self.assertIsNotNone(contact.properties["GivenName"])

    def test_get_contacts(self):
        client = OutlookClient(username=settings['username'], password=settings['password'])
        contacts = client.get_contacts()
        client.load(contacts)
        client.execute_query()
        self.assertGreaterEqual(len(contacts), 1)
