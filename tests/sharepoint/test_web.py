"""Tests for SharePoint web operations including users, permissions, sub-webs, lists, and folders."""

from __future__ import annotations

from datetime import datetime
from random import randint
from typing import ClassVar, Optional

from office365.sharepoint.lists.templates.type import ListTemplateType
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.permissions.kind import PermissionKind
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.webs.creation_information import WebCreationInformation
from office365.sharepoint.webs.subweb_query import SubwebQuery
from office365.sharepoint.webs.web import Web

from tests import test_site_url
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSharePointWeb(SPTestCase):
    """Test SharePoint web features."""

    target_web: ClassVar[Optional[Web]] = None
    target_user: ClassVar[Optional[User]] = None

    def test_01_get_current_user(self):
        """Get the current user."""
        result = self.client.web.current_user.get().execute_query()
        self.assertIsNotNone(result.login_name)
        TestSharePointWeb.target_user = result

    def test_02_get_web_from_page_url(self):
        """Get web URL from a page URL."""
        page_url = f"{test_site_url}/SitePages/Home.aspx"
        result = Web.get_web_url_from_page_url(self.client, page_url).execute_query()
        self.assertIsNotNone(result.value)

    def test_03_get_list_item_by_abs_url(self):
        """Get list item by absolute URL."""
        page_url = f"{test_site_url}/SitePages/Home.aspx"
        result = self.client.web.get_list_item(page_url).execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_04_does_user_has_perms(self):
        """Check if the current user has specific permissions."""
        perms = BasePermissions()
        perms.set(PermissionKind.ManageWeb)
        perms.set(PermissionKind.AddListItems)
        result = self.client.web.does_user_have_permissions(perms).execute_query()
        self.assertIsInstance(result.value, bool)

    def test_05_get_user_permissions(self):
        """Get effective permissions for the target user."""
        target_user = TestSharePointWeb.target_user
        if not target_user:
            self.skipTest("No target user from previous test")
        self.assertIsNotNone(target_user.login_name)
        result = self.client.web.get_user_effective_permissions(target_user.login_name).execute_query()
        self.assertIsInstance(result.value, BasePermissions)

    def test_06_can_create_web(self):
        """Create a new sub-web."""
        target_web_name = "workspace_" + str(randint(0, 100000))
        creation_info = WebCreationInformation()
        creation_info.Url = target_web_name
        creation_info.Title = target_web_name
        TestSharePointWeb.target_web = self.client.web.webs.add(creation_info).execute_query()

        results = self.client.web.webs.filter(f"Title eq '{target_web_name}'").get().execute_query()
        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0].resource_path)

    def test_07_get_sub_web(self):
        """Get sub-webs filtered for the current user."""
        sub_webs = self.client.web.get_sub_webs_filtered_for_current_user(SubwebQuery()).execute_query()
        self.assertGreater(len(sub_webs), 0)

    def test_08_if_web_updated(self):
        """Update a web resource title."""
        target_web = TestSharePointWeb.target_web
        if not target_web:
            self.skipTest("No target web from previous test")
        web_title_updated = target_web.properties["Title"] + "_updated"
        target_web.set_property("Title", web_title_updated)
        target_web.update().execute_query()

        updated_web = target_web.get().execute_query()
        self.assertEqual(web_title_updated, updated_web.properties["Title"])

    def test_09_if_web_deleted(self):
        """Delete a web resource."""
        target_web = TestSharePointWeb.target_web
        if not target_web:
            self.skipTest("No target web from previous test")
        title = target_web.properties["Title"]
        target_web.delete_object().execute_query()

        results = self.client.web.webs.filter(f"Title eq '{title}'").get().execute_query()
        self.assertEqual(len(results), 0)

    def test_10_enum_all_webs(self):
        """Enumerate all webs within the site."""
        webs = self.client.web.get_all_webs().execute_query()
        self.assertGreater(len(webs), 0)

    def test_11_read_list(self):
        """Read a list by its name."""
        site_pages = self.client.web.get_list("SitePages").get().execute_query()
        self.assertIsNotNone(site_pages.title)

    def test_12_get_user_perms(self):
        """Get user effective permissions with levels."""
        target_user = TestSharePointWeb.target_user
        if not target_user:
            self.skipTest("No target user from previous test")
        self.assertIsNotNone(target_user.login_name)
        result = self.client.web.get_user_effective_permissions(target_user.login_name).execute_query()
        self.assertIsInstance(result.value, BasePermissions)
        self.assertGreater(len(result.value.permission_levels), 0)

    def test_13_get_user_by_id(self):
        """Get user by ID."""
        target_user = TestSharePointWeb.target_user
        if not target_user:
            self.skipTest("No target user from previous test")
        self.assertIsNotNone(target_user.id)
        assert target_user.id is not None
        result_user = self.client.web.get_user_by_id(target_user.id).get().execute_query()
        self.assertEqual(result_user.login_name, target_user.login_name)

    def test_14_get_catalog(self):
        """Get the master page catalog."""
        catalog = self.client.web.get_catalog(ListTemplateType.MasterPageCatalog).get().execute_query()
        self.assertIsNotNone(catalog.title)

    def test_15_get_document_libraries(self):
        """Get document libraries for the site."""
        result = Web.get_document_libraries(self.client, test_site_url).execute_query()
        self.assertGreater(len(result.value), 0)

    def test_16_get_document_and_media_libraries(self):
        """Get document and media libraries."""
        result = Web.get_document_and_media_libraries(self.client, test_site_url, True).execute_query()
        self.assertGreater(len(result.value), 0)

    def test_17_get_list_templates(self):
        """Get list templates."""
        templates = self.client.web.list_templates.get().execute_query()
        self.assertGreater(len(templates), 0)

    def test_18_get_custom_list_templates(self):
        """Get custom list templates."""
        templates = self.client.web.get_custom_list_templates().execute_query()
        self.assertGreaterEqual(len(templates), 0)

    def test_19_ensure_folder_path(self):
        """Ensure a nested folder path exists."""
        folder_path = "Shared Documents/Archive/2020/12"
        folder_new_nested = self.client.web.ensure_folder_path(folder_path).execute_query()
        folder_new_nested = self.client.web.get_folder_by_server_relative_url(folder_path).get().execute_query()
        self.assertTrue(folder_new_nested.exists)

    def test_20_get_context_web_theme_data(self):
        """Get context web theme data."""
        result = Web.get_context_web_theme_data(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test_21_get_regional_datetime_schema(self):
        """Get regional datetime schema."""
        result = self.client.web.get_regional_datetime_schema().execute_query()
        self.assertIsNotNone(result.value)

    # def test_23_get_push_notification_subscribers_by_user(self):
    #    current_user = self.client.web.current_user
    #    result = self.client.web.get_push_notification_subscribers_by_user(current_user).execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test_22_get_list_item_by_path(self):
        """Get list item by path."""
        page_url = "SitePages/Home.aspx"
        target_item = self.client.web.get_list_item_using_path(page_url).get().execute_query()
        self.assertIsNotNone(target_item.resource_path)

    def test_23_parse_datetime(self):
        """Parse a datetime string."""
        today = str(datetime.today())
        result = self.client.web.parse_datetime(today).execute_query()
        self.assertIsNotNone(result.value)

    # def test_26_list_acs_service_principals(self):
    #    from office365.sharepoint.client_context import ClientContext
    #    admin_client = ClientContext(test_team_site_url).with_credentials(
    #        test_admin_credentials
    #    )
    #    result = admin_client.web.get_acs_service_principals().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_24_ensure_tenant_app_catalog(self):
        """Ensure the tenant app catalog exists."""
        result = self.client.web.ensure_tenant_app_catalog("app").execute_query()
        self.assertIsNotNone(result.value)

    # def test_28_get_push_notification_subscribers(self):
    #    result = self.client.web.push_notification_subscribers.get().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    # def test_29_ensure_edu_class_setup(self):
    #    result = self.client.web.ensure_edu_class_setup(True).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_30_get_acs_service_principals(self):
    #    result = self.client.web.get_acs_service_principals().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_25_get_access_request_list(self):
        """Get the access request list.

        The list only exists once access requests are enabled on the web; while
        they are off the web carries no ``AccessRequestListUrl`` to follow.
        """
        web = self.client.web.select(["AccessRequestListUrl"]).get().execute_query()
        list_url = web.get_property("AccessRequestListUrl")
        if not list_url:
            self.skipTest("Access requests are not enabled on this web")
        result = self.client.web.get_access_request_list().get().execute_query()
        self.assertIsNotNone(result.resource_path)
