from office365.sharepoint.utilities.email_properties import EmailProperties
from office365.sharepoint.utilities.utility import Utility
from settings import settings
from tests.sharepoint.sharepoint_case import SPTestCase


class TestUtility(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUtility, cls).setUpClass()

    def test1_get_current_user_email_addresses(self):
        result = Utility.get_current_user_email_addresses(self.client)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test2_get_user_permission_levels(self):
        result = Utility.get_user_permission_levels(self.client)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test3_send_email(self):
        email_props = EmailProperties("The new cafeteria is open.", "Meet for lunch?",
                                      [settings.get('first_account_name')])
        Utility.send_email(self.client, email_props)
        self.client.execute_query()
