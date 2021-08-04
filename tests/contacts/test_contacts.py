from office365.outlook.calendar.calendar import Calendar
from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestContacts(GraphTestCase):
    """Tests for Calendar"""

    cal_name = create_unique_name("Volunteer")
    target_cal = None  # type: Calendar

    @classmethod
    def setUpClass(cls):
        super(TestContacts, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_list_contacts(self):
        contacts = self.client.me.contacts.top(10).get().execute_query()
        self.assertIsNotNone(contacts.resource_path)

