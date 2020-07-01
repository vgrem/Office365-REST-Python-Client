import urllib.parse
from unittest import TestCase
from office365.runtime.auth.userCredential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.sharingResult import SharingResult
from office365.sharepoint.ui.applicationpages.clientPeoplePickerQueryParameters import ClientPeoplePickerQueryParameters
from office365.sharepoint.ui.applicationpages.clientPeoplePickerWebServiceInterface import \
    ClientPeoplePickerWebServiceInterface
from office365.sharepoint.webs.web import Web
from settings import settings


class TestSharePointSharing(TestCase):

    @classmethod
    def setUpClass(cls):
        credentials = UserCredential(user_name=settings['user_credentials']['username'],
                                     password=settings['user_credentials']['password'])
        cls.client = ClientContext(settings['url']).with_credentials(credentials)

    def test1_get_object_sharing_settings(self):
        file_abs_url = urllib.parse.urljoin(settings['url'], "/SitePages/Home.aspx")
        result = Web.get_object_sharing_settings(self.client, file_abs_url, 0, True)
        self.client.execute_query()
        self.assertIsNotNone(result.web_url)

    def test2_share_file(self):
        file_abs_url = urllib.parse.urljoin(settings['url'], "/SitePages/Home.aspx")

        current_user = self.client.web.currentUser
        self.client.load(current_user)
        self.client.execute_query()

        params = ClientPeoplePickerQueryParameters(current_user.properties['UserPrincipalName'])
        result = ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(self.client, params)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

        sharing_result = Web.share_object(self.client, file_abs_url, result.value)
        self.client.execute_query()
        self.assertIsInstance(sharing_result, SharingResult)
        self.assertIsNone(sharing_result.errorMessage)
