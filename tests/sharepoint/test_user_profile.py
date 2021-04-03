from unittest import TestCase

from office365.sharepoint.userprofiles.personPropertiesCollection import PersonPropertiesCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.userprofiles.peopleManager import PeopleManager
from office365.sharepoint.userprofiles.profileLoader import ProfileLoader
from tests import test_user_credentials, test_team_site_url, test_user_principal_name


class TestUserProfile(TestCase):
    profile_loader = None  # type: ProfileLoader

    @classmethod
    def setUpClass(cls):
        cls.my_client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

    def test1_get_profile_loader(self):
        profile_loader = ProfileLoader.get_profile_loader(self.my_client).execute_query()
        self.__class__.profile_loader = profile_loader

    def test2_get_profile_loader(self):
        user_profile = self.__class__.profile_loader.get_user_profile().execute_query()
        self.assertIsNotNone(user_profile.properties["AccountName"])

    def test3_create_personal_site(self):
        user_profile = self.__class__.profile_loader.get_user_profile()
        up = user_profile.create_personal_site_enque(True).execute_query()
        self.assertIsNotNone(up.properties['PublicUrl'])

    def test4_get_user_props(self):
        target_user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_user_profile_properties(target_user.login_name)
        self.my_client.execute_query()
        self.assertIsNotNone(result.value)

    def test5_get_properties_for(self):
        me = self.my_client.web.current_user.get().execute_query()
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_properties_for(me.login_name)
        self.my_client.execute_query()
        self.assertIsNotNone(result)

    def test6_get_default_document_library(self):
        me = self.my_client.web.current_user.get().execute_query()
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_default_document_library(me.login_name)
        self.my_client.execute_query()
        self.assertIsNotNone(result.value)

    def test7_get_people_followed_by(self):
        me = self.my_client.web.current_user.get().execute_query()
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_people_followed_by(me.login_name).execute_query()
        self.assertIsNotNone(result)

    def test7_start_stop_following(self):
        people_manager = PeopleManager(self.my_client)
        target_user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()

        result = people_manager.ami_following(target_user.login_name)
        people_manager.execute_query()

        if result.value:
            people_manager.stop_following(target_user.login_name).execute_query()
        else:
            people_manager.follow(target_user.login_name)

    def test8_get_followers_for(self):
        people_manager = PeopleManager(self.my_client)
        target_user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
        result = people_manager.get_followers_for(target_user.login_name)
        people_manager.execute_query()
        self.assertIsInstance(result.value, PersonPropertiesCollection)

    def test9_get_my_followers(self):
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_my_followers().execute_query()
        self.assertIsInstance(result, PersonPropertiesCollection)
