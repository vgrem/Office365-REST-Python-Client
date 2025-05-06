from unittest import TestCase

from office365.runtime.compat import urljoin
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.sharing.document_manager import DocumentSharingManager
from office365.sharepoint.sharing.object_sharing_information import (
    ObjectSharingInformation,
)
from office365.sharepoint.sharing.operation_status_code import (
    SharingOperationStatusCode,
)
from office365.sharepoint.sharing.result import SharingResult
from office365.sharepoint.sharing.role_type import RoleType
from office365.sharepoint.sharing.site_sharing_report_helper import (
    SiteSharingReportHelper,
)
from office365.sharepoint.webs.web import Web
from tests import test_site_url, test_user_credentials


class TestSharePointSharing(TestCase):
    target_user = None  # type: User
    target_file_url = urljoin(test_site_url, "/SitePages/Home.aspx")

    @classmethod
    def setUpClass(cls):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        client.web.lists.ensure_site_pages_library().execute_query()
        current_user = client.web.current_user.get().execute_query()
        cls.target_user = current_user
        cls.client = client

    def test1_get_role_def(self):
        role_def = DocumentSharingManager.get_role_definition(
            self.client, RoleType.Contributor
        ).execute_query()
        self.assertTrue(role_def.name, "Full Control")

    def test2_get_object_sharing_settings(self):
        result = Web.get_object_sharing_settings(
            self.client, self.target_file_url, 0, True
        ).execute_query()
        self.assertIsNotNone(result.web_url)

    def test3_get_file_sharing_info(self):
        list_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        sharing_info = list_item.get_sharing_information().execute_query()
        self.assertIsNotNone(list_item.resource_path)
        self.assertIsInstance(sharing_info, ObjectSharingInformation)

    def test4_share_file(self):
        target_file_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        result = target_file_item.share(
            self.target_user.user_principal_name
        ).execute_query()
        self.assertIsNone(result.error_message)

    def test5_get_shared_with_me_items(self):
        from office365.sharepoint.portal.userprofiles.sharedwithme.item_collection import (
            SharedWithMeItemCollection,
        )

        result = SharedWithMeItemCollection.get_shared_with_me_items(
            self.client, 10
        ).execute_query()
        self.assertIsNotNone(result.value)

    def test6_unshare_file(self):
        target_file_item = self.client.web.get_list_item("/SitePages/Home.aspx")
        result = target_file_item.unshare().execute_query()
        self.assertIsInstance(result, SharingResult)
        self.assertIsNone(result.error_message)

    def test7_share_web(self):
        result = self.client.web.share(
            self.target_user.user_principal_name
        ).execute_query()
        self.assertIsInstance(result, SharingResult)
        self.assertEqual(
            result.status_code, SharingOperationStatusCode.CompletedSuccessfully
        )
        self.assertIsNone(result.error_message)

    def test8_unshare_web(self):
        result = self.client.web.unshare().execute_query()
        self.assertIsInstance(result, SharingResult)

    def test9_get_web_sharing_information(self):
        result = ObjectSharingInformation.get_web_sharing_information(
            self.client
        ).execute_query()
        self.assertIsNotNone(result.properties)

    def test_10_get_site_sharing_report_capabilities(self):
        result = SiteSharingReportHelper.get_site_sharing_report_capabilities(
            self.client
        ).execute_query()
        self.assertIsNotNone(result.value)

    def test_11_get_get_list_sharing_settings(self):
        result = (
            self.client.web.default_document_library()
            .get_sharing_settings()
            .execute_query()
        )
        self.assertIsNotNone(result.list_id)
