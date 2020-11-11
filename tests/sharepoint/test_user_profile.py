from unittest import TestCase

from office365.sharepoint.userprofiles.personPropertiesCollection import PersonPropertiesCollection

from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.userprofiles.peopleManager import PeopleManager
from office365.sharepoint.userprofiles.profileLoader import ProfileLoader


class TestUserProfile(TestCase):
    profile_loader = None  # type: ProfileLoader
    target_account_name = "mdoe@mediadev8.onmicrosoft.com"

    @classmethod
    def setUpClass(cls):
        credentials = UserCredential(settings['user_credentials']['username'],
                                     settings['user_credentials']['password'])
        cls.my_client = ClientContext(settings['url']).with_credentials(credentials)

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
        me = self.my_client.web.currentUser.get().execute_query()
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_user_profile_properties(me.login_name)
        self.my_client.execute_query()
        self.assertIsNotNone(result.value)

    def test5_get_properties_for(self):
        me = self.my_client.web.currentUser.get().execute_query()
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_properties_for(me.login_name)
        self.my_client.execute_query()
        self.assertIsNotNone(result)

    def test6_get_default_document_library(self):
        me = self.my_client.web.currentUser.get().execute_query()
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_default_document_library(me.login_name)
        self.my_client.execute_query()
        self.assertIsNotNone(result.value)

    def test7_get_people_followed_by(self):
        me = self.my_client.web.currentUser.get().execute_query()
        people_manager = PeopleManager(self.my_client)
        result = people_manager.get_people_followed_by(me.login_name).execute_query()
        self.assertIsNotNone(result)

    def test7_start_stop_following(self):
        people_manager = PeopleManager(self.my_client)
        target_user = self.my_client.web.ensure_user(self.__class__.target_account_name).execute_query()

        result = people_manager.ami_following(target_user.login_name)
        people_manager.execute_query()

        if result.value:
            people_manager.stop_following(target_user.login_name).execute_query()
        else:
            people_manager.follow(target_user.login_name)

    def test8_get_followers(self):
        people_manager = PeopleManager(self.my_client)
        target_user = self.my_client.web.ensure_user(self.__class__.target_account_name).execute_query()
        result = people_manager.get_followers_for(target_user.login_name)
        people_manager.execute_query()
        self.assertIsInstance(result.value, PersonPropertiesCollection)
