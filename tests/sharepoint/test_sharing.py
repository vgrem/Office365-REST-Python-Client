from office365.runtime.compat import urljoin
from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.principal.user import User
from office365.sharepoint.sharing.document_sharing_manager import DocumentSharingManager
from office365.sharepoint.sharing.object_sharing_information import ObjectSharingInformation
from office365.sharepoint.sharing.operation_status_code import SharingOperationStatusCode
from office365.sharepoint.sharing.role_type import RoleType
from office365.sharepoint.sharing.sharing_result import SharingResult
from office365.sharepoint.webs.web import Web
from tests import test_site_url, test_user_credentials


class TestSharePointSharing(TestCase):
    target_user = None  # type: User
    target_file_url = urljoin(test_site_url, "/SitePages/Home.aspx")

    @classmethod
    def setUpClass(cls):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        current_user = client.web.current_user.get().execute_query()
        cls.target_user = current_user
        cls.client = client

    def test1_get_role_def(self):
        dsm = DocumentSharingManager(self.client)
        role_def = dsm.get_role_definition(RoleType.Contributor).execute_query()
        self.assertTrue(role_def.name, "Full Control")

    def test2_get_object_sharing_settings(self):
        result = Web.get_object_sharing_settings(self.client, self.target_file_url, 0, True).execute_query()
        self.assertIsNotNone(result.web_url)

    def test3_get_file_sharing_info(self):
        list_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        sharing_info = list_item.get_sharing_information().execute_query()
        self.assertIsNotNone(list_item.resource_path)
        self.assertIsInstance(sharing_info, ObjectSharingInformation)

    def test4_share_file(self):
        target_file_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        result = target_file_item.share(self.target_user.user_principal_name).execute_query()
        self.assertIsNone(result.error_message)

    def test5_unshare_file(self):
        target_file_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        result = target_file_item.unshare().execute_query()
        self.assertIsInstance(result, SharingResult)
        self.assertIsNone(result.error_message)

    def test6_share_web(self):
        result = self.client.web.share(self.target_user.user_principal_name).execute_query()
        self.assertIsInstance(result, SharingResult)
        self.assertEqual(result.status_code, SharingOperationStatusCode.CompletedSuccessfully)
        self.assertIsNone(result.error_message)

    def test7_unshare_web(self):
        result = self.client.web.unshare().execute_query()
        self.assertIsInstance(result, SharingResult)
