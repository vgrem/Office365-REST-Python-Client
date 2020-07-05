from random import randint

from office365.sharepoint.permissions.basePermissions import BasePermissions
from office365.sharepoint.lists.list import List
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType


class TestSPList(SPTestCase):
    target_list = None  # type: List
    target_list_title = "Tasks" + str(randint(0, 10000))

    def test1_get_default_library(self):
        default_lib = self.client.web.default_document_library()
        self.client.load(default_lib)
        self.client.execute_query()
        self.assertIsNotNone(default_lib.properties["Id"])

    def test2_has_library_unique_perms(self):
        default_lib = self.client.web.default_document_library()
        self.client.load(default_lib, ["HasUniqueRoleAssignments"])
        self.client.execute_query()
        self.assertFalse(default_lib.hasUniqueRoleAssignments)

    def test3_library_break_role_inheritance(self):
        default_lib = self.client.web.default_document_library()
        default_lib.break_role_inheritance(False)
        self.client.load(default_lib, ["HasUniqueRoleAssignments"])
        self.client.execute_query()
        self.assertTrue(default_lib.hasUniqueRoleAssignments)

    def test4_library_reset_role_inheritance(self):
        default_lib = self.client.web.default_document_library()
        default_lib.reset_role_inheritance()
        self.client.load(default_lib, ["HasUniqueRoleAssignments"])
        self.client.execute_query()
        self.assertFalse(default_lib.hasUniqueRoleAssignments)

    def test5_create_list(self):
        list_properties = ListCreationInformation()
        list_properties.AllowContentTypes = True
        list_properties.BaseTemplate = ListTemplateType.TasksWithTimelineAndHierarchy
        list_properties.Title = self.target_list_title
        list_to_create = self.client.web.lists.add(list_properties)
        self.client.execute_query()
        self.assertEqual(list_properties.Title, list_to_create.properties['Title'])
        self.__class__.target_list = list_to_create

    def test6_read_list(self):
        list_to_read = self.client.web.lists.get_by_title(self.target_list_title)
        self.client.load(list_to_read)
        self.client.execute_query()
        self.assertEqual(self.target_list_title, list_to_read.properties['Title'])

    def test7_read_list_by_id(self):
        list_to_read = self.client.web.lists.get_by_id(self.__class__.target_list.properties['Id'])
        self.client.load(list_to_read)
        self.client.execute_query()
        self.assertEqual(self.target_list.properties['Id'], list_to_read.properties['Id'])

    def test8_update_list(self):
        list_to_update = self.client.web.lists.get_by_title(self.target_list_title)
        self.target_list_title += "_updated"
        list_to_update.set_property('Title', self.target_list_title)
        list_to_update.update()
        self.client.execute_query()

        result = self.client.web.lists.filter("Title eq '{0}'".format(self.target_list_title))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 1)

    def test9_get_list_permissions(self):
        current_user = self.client.web.currentUser
        self.client.load(current_user)
        self.client.execute_query()
        self.assertIsNotNone(current_user.login_name)

        result = self.__class__.target_list.get_user_effective_permissions(current_user.login_name)
        self.client.execute_query()
        self.assertIsInstance(result.value, BasePermissions)

    def test_10_delete_list(self):
        list_title = self.target_list_title + "_updated"
        list_to_delete = self.client.web.lists.get_by_title(list_title)
        list_to_delete.delete_object()
        self.client.execute_query()

        result = self.client.web.lists.filter("Title eq '{0}'".format(list_title))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 0)
