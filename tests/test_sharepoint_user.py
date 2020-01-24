from tests.sharepoint_case import SPTestCase


class TestSharePointUser(SPTestCase):
    def test_get_current_user(self):
        user = self.context.web.currentUser
        self.context.load(user)
        self.context.execute_query()
        self.assertIsNotNone(user.properties['LoginName'], "Current user was not requested")
        self.assertIsNotNone(user.login_name, "Current user was not requested")
        self.assertIsNotNone(user.resourceUrl)
