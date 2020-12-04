from tests.graph_case import GraphTestCase


class TestOutlookContacts(GraphTestCase):

    def test0_ensure_user_context(self):
        whoami = self.client.me.get().execute_query()
        self.assertIsNotNone(whoami.id)

    def test1_create_contacts(self):
        contact_info = {
            "givenName": "Pavel",
            "surname": "Bansky",
            "emailAddresses": [
                {
                    "address": "pavelb@a830edad9050849NDA1.onmicrosoft.com",
                    "name": "Pavel Bansky"
                }
            ],
            "businessPhones": [
                "+1 732 555 0102"
            ]
        }

        contact = self.client.me.contacts.add_from_json(contact_info).execute_query()
        self.assertIsNotNone(contact.properties["givenName"])

    def test2_get_contacts(self):
        contacts = self.client.me.contacts.get().execute_query()
        self.assertGreaterEqual(len(contacts), 1)

    def test3_update_contact(self):
        results = self.client.me.contacts.top(1).get().execute_query()
        if len(results) == 1:
            contact = results[0]
            self.assertIsNotNone(contact.id)
            contact.set_property("department", "Media").update().execute_query()

    def test4_delete_contact(self):
        results = self.client.me.contacts.top(1).get().execute_query()
        if len(results) == 1:
            contact = results[0]
            contact.delete_object().execute_query()
            # verify
            contacts = self.client.me.contacts.get().execute_query()
            results = [c for c in contacts if c.id == contact.id]
            self.assertEqual(len(results), 0)
