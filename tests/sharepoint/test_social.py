from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.social.rest_following_manager import SocialRestFollowingManager
from tests import test_team_site_url, test_user_credentials
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSocial(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSocial, cls).setUpClass()
        my_client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
        cls.manager = SocialRestFollowingManager(my_client)

    def test_1_get_followers(self):
        result = self.manager.my.followers().execute_query()
        self.assertIsNotNone(result.value)




