from office365.sharepoint.utilities.email_properties import EmailProperties
from office365.sharepoint.utilities.utility import Utility
from tests import test_user_principal_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestUtility(SPTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestUtility, cls).setUpClass()

    def test1_get_current_user_email_addresses(self):
        result = Utility.get_current_user_email_addresses(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test2_get_user_permission_levels(self):
        result = Utility.get_user_permission_levels(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test3_send_email(self):
        email_props = EmailProperties(
            "The new cafeteria is open.", "Meet for lunch?", [test_user_principal_name]
        )
        Utility.send_email(self.client, email_props).execute_query()

    def test4_expand_groups_to_principals(self):
        owner_group = self.client.web.associated_owner_group.get().execute_query()
        result = Utility.expand_groups_to_principals(
            self.client, [owner_group.login_name], 10
        ).execute_query()
        self.assertIsNotNone(result.value)

    def test5_create_email_body_for_invitation(self):
        result = Utility.create_email_body_for_invitation(
            self.client, "SitePages/Home.aspx"
        ).execute_query()
        self.assertIsNotNone(result.value)
