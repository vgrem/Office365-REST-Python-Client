from unittest import TestCase

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.userprofiles.userProfilePropertiesForUser import UserProfilePropertiesForUser
from settings import settings


from office365.sharepoint.userprofiles.profileLoader import ProfileLoader


class TestUserProfile(TestCase):
    profile_loader = None  # type: ProfileLoader

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

    # def test4_get_user_props(self):
    #    account_name = settings['user_credentials']['username']
    #    props = UserProfilePropertiesForUser(self.my_client, account_name, ['PublicUrl'])
    #    self.my_client.load(props)
    #    self.my_client.execute_query()
    #    self.assertIsNotNone(props)
