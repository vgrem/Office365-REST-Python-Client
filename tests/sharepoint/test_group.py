from tests import test_user_principal_name
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.principal.group import Group


class TestSharePointGroup(SPTestCase):
    target_group = None  # type: Group

    @classmethod
    def setUpClass(cls):
        super(TestSharePointGroup, cls).setUpClass()
        cls.target_user = cls.client.web.ensure_user(test_user_principal_name).execute_query()
        cls.target_group = cls.client.web.associated_member_group

    def test1_get_current_user_groups(self):
        groups = self.client.web.current_user.groups.get().execute_query()
        self.assertGreaterEqual(len(groups), 0)

    def test2_add_user_to_group(self):
        target_user = self.target_group.users.add_user(self.target_user.login_name).execute_query()
        self.assertIsNotNone(target_user.id)

    def test3_delete_user_from_group(self):
        target_users = self.target_group.users.get().execute_query()
        users_count_before = len(target_users)
        self.assertGreater(users_count_before, 0)

        user_id = target_users[0].id
        target_users.remove_by_id(user_id)
        self.client.load(target_users)
        self.client.execute_query()
        self.assertEqual(users_count_before, len(target_users) + 1)
