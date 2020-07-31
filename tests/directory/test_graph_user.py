from settings import settings
from tests import random_seed
from tests.graph_case import GraphTestCase

from office365.graph.directory.user import User
from office365.graph.directory.userProfile import UserProfile


class TestGraphUser(GraphTestCase):
    """Tests for Azure Active Directory (Azure AD) users"""

    test_user = None  # type: User

    def test1_get_user_list(self):
        users = self.client.users.top(1)
        self.client.load(users)
        self.client.execute_query()
        self.assertEqual(len(users), 1)
        for user in users:
            self.assertIsNotNone(user.id)

    def test2_create_user(self):
        password = "P@ssw0rd{0}".format(random_seed)
        profile = UserProfile("testuser{0}@{1}".format(random_seed, settings['tenant']), password)
        new_user = self.client.users.add(profile)
        self.client.execute_query()
        self.assertIsNotNone(new_user.id)
        self.__class__.test_user = new_user

    def test3_update_user(self):
        user_to_update = self.__class__.test_user
        prop_name = 'city'
        prop_val = 'Earth{0}'.format(random_seed)
        user_to_update.set_property(prop_name, prop_val)
        user_to_update.update()
        self.client.execute_query()

        result = self.client.users.filter("{0} eq '{1}'".format(prop_name, prop_val))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(1, len(result))

    def test4_delete_user(self):
        user_to_delete = self.__class__.test_user
        user_to_delete.delete_object(True)
        self.client.execute_query()
