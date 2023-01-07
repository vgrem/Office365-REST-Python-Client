from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.userprofiles.my_site_links import MySiteLinks
from office365.sharepoint.userprofiles.people_manager import PeopleManager
from tests import test_user_credentials, test_team_site_url, test_user_principal_name


class TestUserProfile(TestCase):

    promoted_links = None

    @classmethod
    def setUpClass(cls):
        cls.my_client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

    #def test1_get_owner_user_profile(self):
    #    from office365.sharepoint.userprofiles.profile_loader import ProfileLoader
    #    up = ProfileLoader.get_owner_user_profile(self.my_client).execute_query()
    #    self.assertIsNotNone(up.resource_path)

    def test2_get_profile_loader(self):
        user_profile = self.my_client.profile_loader.get_user_profile().execute_query()
        self.assertIsNotNone(user_profile.account_name)

    def test3_create_personal_site(self):
        user_profile = self.my_client.profile_loader.get_user_profile()
        up = user_profile.create_personal_site_enque(True).execute_query()
        self.assertIsNotNone(up.public_url)

    def test4_get_user_props(self):
        target_user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
        result = self.my_client.people_manager.get_user_profile_properties(target_user.login_name).execute_query()
        self.assertIsNotNone(result.value)

    def test5_get_properties_for(self):
        me = self.my_client.web.current_user
        properties = self.my_client.people_manager.get_properties_for(me).execute_query()
        self.assertIsNotNone(properties)

    def test6_get_default_document_library(self):
        me = self.my_client.web.current_user
        result = self.my_client.people_manager.get_default_document_library(me).execute_query()
        self.assertIsNotNone(result.value)

    def test7_get_people_followed_by(self):
        me = self.my_client.web.current_user.get().execute_query()
        result = self.my_client.people_manager.get_people_followed_by(me.login_name).execute_query()
        self.assertIsNotNone(result)

    def test7_start_stop_following(self):
        people_manager = PeopleManager(self.my_client)
        target_user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
        result = people_manager.am_i_following(target_user.login_name).execute_query()
        if result.value:
            people_manager.stop_following(target_user.login_name).execute_query()
        else:
            people_manager.follow(target_user.login_name).execute_query()

    def test8_get_followers_for(self):
        target_user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
        col = self.my_client.people_manager.get_followers_for(target_user.login_name).execute_query()
        self.assertGreaterEqual(len(col), 0)

    def test9_get_my_followers(self):
        col = self.my_client.people_manager.get_my_followers().execute_query()
        self.assertGreaterEqual(len(col), 0)

    def test_10_get_trending_tags(self):
        result = PeopleManager.get_trending_tags(self.my_client).execute_query()
        self.assertGreaterEqual(len(result.items), 0)

    def test_11_get_user_profile_properties(self):
        user_props = self.my_client.web.current_user.get_user_profile_properties().get().execute_query()
        self.assertIsNotNone(user_props.resource_path)

        result = user_props.get_property_names().execute_query()
        self.assertIsNotNone(result.value)

    def test_12_get_my_site_links(self):
        result = MySiteLinks.get_my_site_links(self.my_client).execute_query()
        self.assertIsNotNone(result.all_documents_link)

    #def test_13_set_single_value_profile_property(self):
    #    user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
    #    self.my_client.people_manager.\
    #        set_single_value_profile_property(user.login_name, "Country", "Finland").execute_query()

    def test_14_add_site_link(self):
        from office365.sharepoint.userprofiles.promoted_sites import PromotedSites
        PromotedSites.add_site_link(self.my_client, "https://www.google.com", "Google").execute_query()

    def test_15_get_promoted_links_as_tiles(self):
        from office365.sharepoint.userprofiles.promoted_sites import PromotedSites
        result = PromotedSites.get_promoted_links_as_tiles(self.my_client).execute_query()
        self.assertIsNotNone(result.value)
        self.assertGreater(len(result.value), 0)
        self.__class__.promoted_links = result.value

    def test_16_get_promoted_links_as_tiles(self):
        from office365.sharepoint.userprofiles.promoted_sites import PromotedSites
        for promoted_link in self.__class__.promoted_links:
            PromotedSites.delete_site_link(self.my_client, promoted_link.ID)
        self.my_client.execute_batch()
        after_result = PromotedSites.get_promoted_links_as_tiles(self.my_client).execute_query()
        self.assertEqual(len(after_result.value), 0)
