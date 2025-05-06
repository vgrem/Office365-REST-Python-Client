from random import randint

from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.currency import CurrencyList
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.template_type import ListTemplateType
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.sharing.role_type import RoleType
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPList(SPTestCase):
    target_list = None  # type: List
    target_list_title = "Tasks" + str(randint(0, 10000))

    @classmethod
    def setUpClass(cls):
        super(TestSPList, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test2_has_library_unique_perms(self):
        default_lib = self.client.web.default_document_library()
        default_lib.reset_role_inheritance()
        self.client.load(default_lib, ["HasUniqueRoleAssignments"])
        self.client.execute_query()
        self.assertFalse(default_lib.has_unique_role_assignments)

    def test3_has_library_unique_perms_chaining(self):
        default_lib = (
            self.client.web.default_document_library()
            .select(["HasUniqueRoleAssignments"])
            .get()
            .execute_query()
        )
        self.assertFalse(default_lib.has_unique_role_assignments)

    def test4_library_break_role_inheritance(self):
        default_lib = self.client.web.default_document_library()
        default_lib.break_role_inheritance(False)
        self.client.load(default_lib, ["HasUniqueRoleAssignments"])
        self.client.execute_query()
        self.assertTrue(default_lib.has_unique_role_assignments)

    def test5_library_add_unique_perms(self):
        target_role_def = self.client.web.role_definitions.get_by_type(
            RoleType.Contributor
        )
        target_user = self.client.web.current_user
        target_lib = self.client.web.default_document_library()
        target_lib.add_role_assignment(target_user, target_role_def).execute_query()

    def test6_library_get_unique_perms(self):
        target_lib = self.client.web.default_document_library()
        target_user = self.client.web.current_user
        assignment = target_lib.get_role_assignment(target_user).get().execute_query()
        self.assertIsNotNone(assignment.principal_id)

    def test6_library_remove_unique_perms(self):
        target_role_def = self.client.web.role_definitions.get_by_type(
            RoleType.Contributor
        )
        target_user = self.client.web.current_user
        target_lib = self.client.web.default_document_library()
        target_lib.remove_role_assignment(target_user, target_role_def).execute_query()

    def test7_library_reset_role_inheritance(self):
        default_lib = self.client.web.default_document_library()
        default_lib.reset_role_inheritance()
        self.client.load(default_lib, ["HasUniqueRoleAssignments"])
        self.client.execute_query()
        self.assertFalse(default_lib.has_unique_role_assignments)

    def test8_create_list(self):
        list_properties = ListCreationInformation()
        list_properties.AllowContentTypes = True
        list_properties.BaseTemplate = ListTemplateType.TasksWithTimelineAndHierarchy
        list_properties.Title = self.target_list_title
        list_to_create = self.client.web.lists.add(list_properties).execute_query()
        self.assertEqual(list_properties.Title, list_to_create.title)
        self.__class__.target_list = list_to_create

    def test9_read_list_by_title(self):
        list_to_read = (
            self.client.web.lists.get_by_title(self.target_list_title)
            .get()
            .execute_query()
        )
        self.assertEqual(self.target_list_title, list_to_read.title)

    def test_10_read_list_by_id(self):
        list_to_read = (
            self.client.web.lists.get_by_id(self.__class__.target_list.id)
            .get()
            .execute_query()
        )
        self.assertEqual(self.target_list.id, list_to_read.id)

    def test_11_read_list_fields(self):
        fields = self.__class__.target_list.get_related_fields().get().execute_query()
        self.assertGreater(len(fields), 0)

    def test_12_update_list(self):
        list_to_update = self.__class__.target_list
        self.target_list_title += "_updated"
        list_to_update.set_property(
            "Title", self.target_list_title
        ).update().execute_query()

        result = (
            self.client.web.lists.filter(
                "Title eq '{0}'".format(self.target_list_title)
            )
            .get()
            .execute_query()
        )
        self.assertEqual(len(result), 1)

    def test_13_get_list_permissions(self):
        current_user = self.client.web.current_user
        result = self.__class__.target_list.get_user_effective_permissions(
            current_user
        ).execute_query()
        self.assertIsInstance(result.value, BasePermissions)

    def test_14_get_list_changes(self):
        changes = self.__class__.target_list.get_changes().execute_query()
        self.assertGreater(len(changes), 0)

    # def test_15_get_checked_out_files(self):
    #    result = self.__class__.target_list.get_checked_out_files().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test_15_delete_list(self):
        list_title = self.target_list_title + "_updated"
        self.client.web.lists.get_by_title(list_title).delete_object().execute_query()

        result = (
            self.client.web.lists.filter("Title eq '{0}'".format(list_title))
            .get()
            .execute_query()
        )
        self.assertEqual(len(result), 0)

    def test_16_get_list_using_path(self):
        pages_list = self.client.web.get_list_using_path("SitePages").execute_query()
        self.assertIsNotNone(pages_list.resource_path)

    def test_17_ensure_events_list(self):
        events_list = self.client.web.lists.ensure_events_list().execute_query()
        self.assertIsNotNone(events_list.resource_path)

    def test_18_get_list_by_server_relative_url(self):
        pages_list = self.client.web.get_list("SitePages").get().execute_query()
        self.assertIsNotNone(pages_list.resource_path)

    def test_19_get_currency_list(self):
        result = CurrencyList.get_list(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test_20_create_document(self):
        lib = self.client.web.default_document_library()
        result = lib.create_document_and_get_edit_link().execute_query()
        self.assertIsNotNone(result.value)

    def test_21_get_list_by_title(self):
        site_pages = (
            self.client.web.get_list_by_title("Site Pages").get().execute_query()
        )
        self.assertIsNotNone(site_pages.resource_path)

    def test_22_get_metadata_navigation_settings(self):
        site_pages = self.client.web.get_list_by_title("Site Pages")
        result = site_pages.get_metadata_navigation_settings().execute_query()
        self.assertIsNotNone(result.value)

    def test_23_render_list_data_as_stream(self):
        result = (
            self.client.web.get_list_by_title("Site Pages")
            .render_list_data_as_stream()
            .execute_query()
        )
        self.assertIsInstance(result.value, dict)

    def test_24_get_compliance_tag(self):
        site_pages = self.client.web.get_list_by_title("Site Pages")
        result = site_pages.get_compliance_tag().execute_query()
        self.assertIsNotNone(result.value)
