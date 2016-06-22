from tests.sharepoint_case import SPTestCase


class TestUser(SPTestCase):
    def test_get_current_user_groups(self):
        groups = self.context.web.current_user.groups
        self.context.load(groups)
        self.context.execute_query()
        self.assertGreaterEqual(len(groups), 0)
