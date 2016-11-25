from unittest import TestCase

from client.office365.outlookservices.outlook_client import OutlookClient
from client.office365.runtime.auth.network_credential_context import NetworkCredentialContext
from examples.settings import settings


class TestOutlookClient(TestCase):
    @classmethod
    def setUpClass(cls):
        ctx_auth = NetworkCredentialContext(username=settings['username'], password=settings['password'])
        cls.client = OutlookClient(ctx_auth)

    def test1_create_contacts(self):
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

        contact = self.client.me.contacts.add_from_json(contact_info)
        self.client.execute_query()
        self.assertIsNotNone(contact.properties["GivenName"])

    def test2_get_contacts(self):
        contacts = self.client.me.contacts
        self.client.load(contacts)
        self.client.execute_query()
        self.assertGreaterEqual(len(contacts), 1)

    def test3_update_contact(self):
        results = self.client.me.contacts.top(1)
        self.client.load(results)
        self.client.execute_query()
        if len(results) == 1:
            contact = results[0]
            self.assertIsNotNone(contact.url)
            contact.set_property("Department", "Media")
            contact.update()
            self.client.execute_query()

    def test4_delete_contact(self):
        results = self.client.me.contacts.top(1)
        self.client.load(results)
        self.client.execute_query()
        if len(results) == 1:
            contact = results[0]
            contact.delete_object()
            self.client.execute_query()
            # verify
            contacts = self.client.me.contacts
            self.client.load(contacts)
            self.client.execute_query()
            results = [c for c in contacts if c.contact_id == contact.contact_id]
            self.assertEqual(len(results), 0)
