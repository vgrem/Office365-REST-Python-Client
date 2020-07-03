import urllib.parse
from unittest import TestCase
from office365.runtime.auth.userCredential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.principal.user import User
from office365.sharepoint.sharing.sharingResult import SharingResult
from office365.sharepoint.webs.web import Web
from settings import settings


class TestSharePointSharing(TestCase):
    target_user = None  # type: User
    target_file_url = urllib.parse.urljoin(settings['url'], "/SitePages/Home.aspx")

    @classmethod
    def setUpClass(cls):
        credentials = UserCredential(user_name=settings['user_credentials']['username'],
                                     password=settings['user_credentials']['password'])
        cls.client = ClientContext(settings['url']).with_credentials(credentials)

        current_user = cls.client.web.currentUser
        cls.client.load(current_user)
        cls.client.execute_query()
        cls.target_user = current_user

    def test1_get_object_sharing_settings(self):
        result = Web.get_object_sharing_settings(self.client, self.target_file_url, 0, True)
        self.client.execute_query()
        self.assertIsNotNone(result.web_url)

    def test2_share_file(self):
        result = Web.share_file(self.client, self.target_file_url, self.target_user.properties['UserPrincipalName'])
        self.client.execute_query()
        self.assertIsInstance(result, SharingResult)

    def test3_unshare_file(self):
        result = Web.unshare_object(self.client, self.target_file_url)
        self.client.execute_query()
        self.assertIsInstance(result, SharingResult)
        self.assertIsNone(result.errorMessage)

    def test4_share_web(self):
        result = self.client.web.share(self.target_user.properties['UserPrincipalName'])
        self.client.execute_query()
        self.assertIsInstance(result, SharingResult)

    def test5_unshare_web(self):
        result = self.client.web.unshare()
        self.client.execute_query()
        self.assertIsInstance(result, SharingResult)
