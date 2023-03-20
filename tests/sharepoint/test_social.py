from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.social.following.rest_manager import SocialRestFollowingManager
from office365.sharepoint.social.switch import SPSocialSwitch
from tests import test_team_site_url, test_user_credentials
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSocial(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSocial, cls).setUpClass()
        cls.my_client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

    def test1_is_following_feature_enabled(self):
        result = SPSocialSwitch.is_following_feature_enabled(self.my_client).execute_query()
        self.assertIsNotNone(result.value)

    def test3_create_post(self):
        # post_data = SocialPostCreationData(content_text="Look at this!")
        # manager = SocialFeedManager(self.my_client)
        # result = manager.create_post(None, post_data).execute_query()
        # self.assertIsNotNone(result.value)
        pass

    def test4_delete_post(self):
        pass

    def test5_get_followers(self):
        manager = SocialRestFollowingManager(self.my_client)
        result = manager.my.followers().execute_query()
        self.assertIsNotNone(result.value)

    def test6_get_followers_alt(self):
        result = self.my_client.social_following_manager.get_followers().execute_query()
        self.assertIsNotNone(result.value)

    def test7_get_suggestions(self):
        result = self.my_client.social_following_manager.get_suggestions().execute_query()
        self.assertIsNotNone(result.value)

    #def test8_get_social_feed(self):
    #    feed = SocialRestFeed(self.my_client).get().execute_query()
    #    self.assertIsNotNone(feed.social_feed)

    #def test9_get_feed(self):
    #    result = self.my_client.social_feed_manager.get_feed().execute_query()
    #    self.assertIsNotNone(result.value)
