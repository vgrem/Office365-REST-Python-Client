from tests.sharepoint.sharepoint_case import SPTestCase


class TestSharePointGroup(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSharePointGroup, cls).setUpClass()
        cls.target_user_name = "i:0#.f|membership|mdoe@mediadev8.onmicrosoft.com"
        cls.target_group = cls.client.web.associatedMemberGroup

    def test1_get_current_user_groups(self):
        groups = self.client.web.currentUser.groups
        self.client.load(groups)
        self.client.execute_query()
        self.assertGreaterEqual(len(groups), 0)

    def test2_add_user_to_group(self):
        target_user = self.target_group.users.add_user(self.target_user_name)
        self.client.execute_query()
        self.assertIsNotNone(target_user.properties['Id'])

    def test3_delete_user_from_group(self):
        target_users = self.target_group.users
        self.client.load(target_users)
        self.client.execute_query()
        users_count_before = len(target_users)
        self.assertGreater(users_count_before, 0)

        user_id = target_users[0].properties['Id']
        target_users.remove_by_id(user_id)
        self.client.load(target_users)
        self.client.execute_query()
        self.assertEqual(users_count_before, len(target_users) + 1)
