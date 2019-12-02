from tests.sharepoint_case import SPTestCase


class TestUser(SPTestCase):
    def test_get_current_user_groups(self):
        groups = self.context.web.current_user.groups
        self.context.load(groups)
        self.context.execute_query()
        self.assertGreaterEqual(len(groups), 0)

    def test_2_add_user_to_group(self):
        test_login_name = "i:0#.f|membership|mdoe@mediadev8.onmicrosoft.com"
        target_group = self.context.web.site_groups.get_by_name("Communication site Visitors")
        user = target_group.users.add_user(test_login_name)
        self.context.execute_query()
        self.assertIsNotNone(user.properties['Id'])
