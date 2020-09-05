import urllib.parse
from unittest import TestCase

from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.principal.user import User
from office365.sharepoint.sharing.objectSharingInformation import ObjectSharingInformation
from office365.sharepoint.sharing.sharingResult import SharingResult
from office365.sharepoint.webs.web import Web


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

    # def test1_get_role_def(self):
    #    dsm = DocumentSharingManager(self.client)
    #    role_def = dsm.get_role_definition(RoleType.View)
    #    self.client.execute_query()
    #    self.assertIsInstance(role_def, RoleDefinition)
    #    self.assertTrue(role_def.name, "Read")

    def test2_get_object_sharing_settings(self):
        result = Web.get_object_sharing_settings(self.client, self.target_file_url, 0, True)
        self.client.execute_query()
        self.assertIsNotNone(result.web_url)

    def test3_get_file_sharing_info(self):
        list_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        sharing_info = list_item.get_sharing_information()
        self.client.execute_query()
        self.assertIsNotNone(list_item.resource_path)
        self.assertIsInstance(sharing_info, ObjectSharingInformation)

    def test4_share_file(self):
        target_file_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        result = target_file_item.share(self.target_user.properties['UserPrincipalName'])
        self.client.execute_query()
        self.assertIsInstance(result, SharingResult)

    def test5_unshare_file(self):
        target_file_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        result = target_file_item.unshare()
        self.client.execute_query()
        self.assertIsInstance(result, SharingResult)
        self.assertIsNone(result.errorMessage)

    def test6_share_web(self):
        result = self.client.web.share(self.target_user.properties['UserPrincipalName'])
        self.client.execute_query()
        self.assertIsInstance(result, SharingResult)

    def test7_unshare_web(self):
        result = self.client.web.unshare()
        self.client.execute_query()
        self.assertIsInstance(result, SharingResult)
