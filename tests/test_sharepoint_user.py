from tests.sharepoint_case import SPTestCase


class TestSharePointUser(SPTestCase):
    target_user_name = None

    def test1_get_current_user(self):
        user = self.client.web.currentUser
        self.client.load(user)
        self.client.execute_query()
        self.assertIsNotNone(user.properties['LoginName'], "Current user was not requested")
        self.assertIsNotNone(user.login_name, "Current user was not requested")
        self.assertIsNotNone(user.resourcePath)
        self.__class__.target_user_name = user.properties['LoginName']

    def test2_ensure_user(self):
        self.client.web.ensureUser(self.__class__.target_user_name)
        self.client.execute_query()

    def test3_get_user(self):
        target_user = self.client.web.siteUsers.get_by_login_name(self.__class__.target_user_name)
        self.client.load(target_user)
        self.client.execute_query()
        self.assertIsNotNone(target_user.properties['Id'])
