from unittest import TestCase

from client.office365.outlookservices.outlook_client import OutlookClient
from client.office365.runtime.auth.network_credential_context import NetworkCredentialContext
from examples.settings import settings


class TestOutlookClient(TestCase):

    @classmethod
    def setUpClass(cls):
        ctx_auth = NetworkCredentialContext(username=settings['username'], password=settings['password'])
        cls.client = OutlookClient(ctx_auth)

    def test_create_contacts(self):
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

        contact = self.client.contacts.add(contact_info)
        self.client.execute_query()
        self.assertIsNotNone(contact.properties["GivenName"])

    def test_get_contacts(self):
        contacts = self.client.contacts
        self.client.load(contacts)
        self.client.execute_query()
        self.assertGreaterEqual(len(contacts), 1)

    def test_update_contact(self):
        results = self.client.contacts.top(1)
        self.client.load(results)
        self.client.execute_query()
        if len(results) == 1:
            contact = results[0]
            contact.set_property("Department", "Media")
            contact.update()
            self.client.execute_query()
