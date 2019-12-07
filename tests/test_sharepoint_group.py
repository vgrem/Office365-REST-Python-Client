from tests.sharepoint_case import SPTestCase


class TestSharePointGroup(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSharePointGroup, cls).setUpClass()
        cls.target_user_name = "i:0#.f|membership|mdoe@mediadev8.onmicrosoft.com"
        cls.target_group_name = "Communication site Visitors"

    def test_1_get_current_user_groups(self):
        groups = self.context.web.current_user.groups
        self.context.load(groups)
        self.context.execute_query()
        self.assertGreaterEqual(len(groups), 0)

    def test_2_add_user_to_group(self):
        target_group = self.context.web.site_groups.get_by_name(self.target_group_name)
        target_user = target_group.users.add_user(self.target_user_name)
        self.context.execute_query()
        self.assertIsNotNone(target_user.properties['Id'])

    def test_3_delete_user_from_group(self):
        target_group = self.context.web.site_groups.get_by_name(self.target_group_name)
        target_users = target_group.users
        self.context.load(target_users)
        self.context.execute_query()
        users_count_before = len(target_users)
        self.assertGreater(users_count_before, 0)

        user_id = target_users[0].properties['Id']
        target_users.remove_by_id(user_id)
        self.context.load(target_users)
        self.context.execute_query()

        self.assertEqual(users_count_before, len(target_users) + 1)
