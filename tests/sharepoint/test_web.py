from datetime import datetime
from random import randint

from tests import test_site_url
from tests.sharepoint.sharepoint_case import SPTestCase
from office365.sharepoint.lists.template_type import ListTemplateType
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.permissions.kind import PermissionKind
from office365.sharepoint.principal.user import User
from office365.sharepoint.webs.subweb_query import SubwebQuery
from office365.sharepoint.webs.web import Web
from office365.sharepoint.webs.creation_information import WebCreationInformation


class TestSharePointWeb(SPTestCase):
    target_web = None  # type: Web
    target_user = None  # type: User

    @classmethod
    def setUpClass(cls):
        super(TestSharePointWeb, cls).setUpClass()

    def test1_get_current_user(self):
        current_user = self.client.web.current_user.get().execute_query()
        self.assertIsNotNone(current_user.login_name)
        self.__class__.target_user = current_user

    def test2_get_web_from_page_url(self):
        page_url = "{site_url}/SitePages/Home.aspx".format(site_url=test_site_url)
        result = Web.get_web_url_from_page_url(self.client, page_url).execute_query()
        self.assertIsNotNone(result.value)

    def test3_get_list_item_by_url(self):
        page_url = "{site_url}/SitePages/Home.aspx".format(site_url=test_site_url)
        target_item = self.client.web.get_list_item(page_url).execute_query()
        self.assertIsNotNone(target_item.resource_path)

    def test4_does_user_has_perms(self):
        perms = BasePermissions()
        perms.set(PermissionKind.ManageWeb)
        result = self.client.web.does_user_have_permissions(perms).execute_query()
        self.assertIsInstance(result.value, bool)

    def test5_get_user_permissions(self):
        result = self.client.web.get_user_effective_permissions(self.__class__.target_user.login_name).execute_query()
        self.assertIsInstance(result.value, BasePermissions)

    def test6_can_create_web(self):
        target_web_name = "workspace_" + str(randint(0, 100000))
        creation_info = WebCreationInformation()
        creation_info.Url = target_web_name
        creation_info.Title = target_web_name
        self.__class__.target_web = self.client.web.webs.add(creation_info).execute_query()

        results = self.client.web.webs.filter("Title eq '{0}'".format(target_web_name)).get().execute_query()
        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0].resource_path)

    def test7_get_sub_web(self):
        sub_webs = self.client.web.get_sub_webs_filtered_for_current_user(SubwebQuery()).execute_query()
        self.assertGreater(len(sub_webs), 0)

    def test8_if_web_updated(self):
        """Test to update Web resource"""
        web_title_updated = self.__class__.target_web.properties["Title"] + "_updated"
        self.__class__.target_web.set_property("Title", web_title_updated)
        self.__class__.target_web.update().execute_query()

        updated_web = self.__class__.target_web.get().execute_query()
        self.assertEqual(web_title_updated, updated_web.properties['Title'])

    def test9_if_web_deleted(self):
        """Test to delete Web resource"""
        title = self.__class__.target_web.properties['Title']
        self.__class__.target_web.delete_object().execute_query()

        results = self.client.web.webs.filter("Title eq '{0}'".format(title)).get().execute_query()
        self.assertEqual(len(results), 0)

    def test_10_enum_all_webs(self):
        """Test to enumerate all webs within site"""
        webs = self.client.web.get_all_webs().execute_query()
        self.assertTrue(len(webs) > 0)

    def test_11_read_list(self):
        site_pages = self.client.web.get_list("SitePages").get().execute_query()
        self.assertIsNotNone(site_pages.title)

    def test_12_get_user_perms(self):
        result = self.client.web.get_user_effective_permissions(self.__class__.target_user.login_name).execute_query()
        self.assertIsInstance(result.value, BasePermissions)
        self.assertGreater(len(result.value.permission_levels), 0)

    def test_13_get_user_by_id(self):
        result_user = self.client.web.get_user_by_id(self.__class__.target_user.id).get().execute_query()
        self.assertEqual(result_user.login_name, self.__class__.target_user.login_name)

    def test_14_get_catalog(self):
        catalog = self.client.web.get_catalog(ListTemplateType.MasterPageCatalog).get().execute_query()
        self.assertIsNotNone(catalog.title)

    def test_15_get_document_libraries(self):
        result = Web.get_document_libraries(self.client, test_site_url).execute_query()
        self.assertGreater(len(result.value), 0)

    def test_16_get_document_and_media_libraries(self):
        result = Web.get_document_and_media_libraries(self.client, test_site_url, True).execute_query()
        self.assertGreater(len(result.value), 0)

    def test_17_get_available_web_templates(self):
        templates = self.client.web.get_available_web_templates().execute_query()
        self.assertGreater(len(templates), 0)

    def test_18_get_list_templates(self):
        templates = self.client.web.list_templates.get().execute_query()
        self.assertGreater(len(templates), 0)

    def test_19_get_custom_list_templates(self):
        templates = self.client.web.get_custom_list_templates().execute_query()
        self.assertGreaterEqual(len(templates), 0)

    def test_20_ensure_folder_path(self):
        folder_path = "Shared Documents/Archive/2020/12"
        folder_new_nested = self.client.web.ensure_folder_path(folder_path).execute_query()
        folder_new_nested = self.client.web.get_folder_by_server_relative_url(folder_path).get().execute_query()
        self.assertTrue(folder_new_nested.exists)

    def test_21_get_context_web_theme_data(self):
        result = Web.get_context_web_theme_data(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test_22_get_regional_datetime_schema(self):
        result = self.client.web.get_regional_datetime_schema().execute_query()
        self.assertIsNotNone(result.value)

    def test_23_get_push_notification_subscribers_by_user(self):
        #current_user = self.client.web.current_user
        #result = self.client.web.get_push_notification_subscribers_by_user(current_user).execute_query()
        #self.assertIsNotNone(result.resource_path)
        pass

    def test_24_get_list_item_by_path(self):
        page_url = "SitePages/Home.aspx"
        target_item = self.client.web.get_list_item_using_path(page_url).get().execute_query()
        self.assertIsNotNone(target_item.resource_path)

    def test_25_parse_datetime(self):
        today = str(datetime.today())
        result = self.client.web.parse_datetime(today).execute_query()
        self.assertIsNotNone(result.value)

    def test_26_list_acs_service_principals(self):
        result = self.client.web.list_acs_service_principals().execute_query()
        self.assertIsNotNone(result.value)
