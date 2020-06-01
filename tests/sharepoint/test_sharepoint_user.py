from tests.sharepoint.sharepoint_case import SPTestCase


class TestSharePointUser(SPTestCase):
    target_user_name = None

    def test1_get_current_user(self):
        user = self.client.web.currentUser
        self.client.load(user)
        self.client.execute_query()
        self.assertIsNotNone(user.properties['LoginName'], "Current user was not requested")
        self.assertIsNotNone(user.login_name, "Current user was not requested")
        self.assertIsNotNone(user.resource_path)
        self.__class__.target_user_name = user.properties['LoginName']

    def test2_ensure_user(self):
        self.client.web.ensure_user(self.__class__.target_user_name)
        self.client.execute_query()

    def test3_get_user(self):
        target_user = self.client.web.siteUsers.get_by_login_name(self.__class__.target_user_name)
        self.client.load(target_user)
        self.client.execute_query()
        self.assertIsNotNone(target_user.properties['Id'])

    def test4_get_user_permissions(self):
        perms_result = self.client.web.get_user_effective_permissions(self.__class__.target_user_name)
        self.client.execute_query()
        self.assertIsNotNone(perms_result.value)
