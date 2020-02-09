from tests.sharepoint_case import SPTestCase


class TestSharePointUser(SPTestCase):
    def test1_get_current_user(self):
        user = self.client.web.currentUser
        self.client.load(user)
        self.client.execute_query()
        self.assertIsNotNone(user.properties['LoginName'], "Current user was not requested")
        self.assertIsNotNone(user.login_name, "Current user was not requested")
        self.assertIsNotNone(user.resourceUrl)
