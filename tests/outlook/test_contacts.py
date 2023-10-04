from office365.outlook.contacts.contact import Contact
from tests.graph_case import GraphTestCase


class TestOutlookContacts(GraphTestCase):
    target_contact = None  # type: Contact

    def test0_ensure_user_context(self):
        who_am_i = self.client.me.get().execute_query()
        self.assertIsNotNone(who_am_i.id)

    def test1_create_contacts(self):
        new_contact = self.client.me.contacts.add(
            "Pavel",
            "Bansky",
            "pavelb@a830edad9050849NDA1.onmicrosoft.com",
            "+1 732 555 0102",
        ).execute_query()
        self.assertEqual(new_contact.email_addresses[0].name, "Pavel Bansky")
        self.__class__.target_contact = new_contact

    def test2_list_contacts(self):
        contacts = self.client.me.contacts.get().execute_query()
        self.assertGreaterEqual(len(contacts), 1)

    def test3_update_contact(self):
        contact = self.__class__.target_contact
        self.assertIsNotNone(contact.id)
        contact.set_property("department", "Media").update().execute_query()

    def test4_delete_contact(self):
        contact_to_delete = self.__class__.target_contact
        contact_to_delete.delete_object().execute_query()
        # verify
        contacts = self.client.me.contacts.get().execute_query()
        results = [c for c in contacts if c.id == contact_to_delete.id]
        self.assertEqual(len(results), 0)
