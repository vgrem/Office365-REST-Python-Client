from office365.runtime.client_value_collection import ClientValueCollection
from tests import create_unique_name, test_tenant
from tests.graph_case import GraphTestCase

from office365.directory.user import User
from office365.directory.userProfile import UserProfile


class TestGraphUser(GraphTestCase):
    """Tests for Azure Active Directory (Azure AD) users"""

    test_user = None  # type: User

    def test1_get_user_list(self):
        users = self.client.users.top(1).get().execute_query()
        self.assertEqual(len(users), 1)
        for user in users:
            self.assertIsNotNone(user.id)

    def test2_create_user(self):
        login = create_unique_name("testuser")
        password = create_unique_name("P@ssw0rd")
        profile = UserProfile("{0}@{1}".format(login, test_tenant), password)
        new_user = self.client.users.add(profile).execute_query()
        self.assertIsNotNone(new_user.id)
        self.__class__.test_user = new_user

    def test3_get_user_properties(self):
        user = self.__class__.test_user.select(["assignedLicenses"]).get().execute_query()
        self.assertIsInstance(user.assigned_licenses, ClientValueCollection)

    def test4_user_add_license(self):
        skus = self.client.subscribed_skus.get().execute_query()
        self.assertIsNotNone(skus.resource_path)

    def test5_user_remove_license(self):
        pass

    def test6_update_user(self):
        user_to_update = self.__class__.test_user
        prop_name = 'city'
        prop_val = create_unique_name("city_")
        user_to_update.set_property(prop_name, prop_val).update().execute_query()

        result = self.client.users.filter("{0} eq '{1}'".format(prop_name, prop_val)).get().execute_query()
        self.assertEqual(1, len(result))

    def test7_delete_user(self):
        user_to_delete = self.__class__.test_user
        user_to_delete.delete_object(True).execute_query()
