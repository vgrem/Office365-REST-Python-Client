from office365.directory.administrative_unit import AdministrativeUnit
from office365.runtime.client_value_collection import ClientValueCollection
from tests.graph_case import GraphTestCase


class TestDirectory(GraphTestCase):
    administrative_unit = None  # type: AdministrativeUnit

    def test2_get_deleted_groups(self):
        deleted_groups = self.client.directory.deleted_groups.get().execute_query()
        self.assertEqual(deleted_groups.resource_path.segment, "microsoft.graph.group")

    def test3_get_deleted_users(self):
        deleted_users = self.client.directory.deleted_users.get().execute_query()
        self.assertEqual(deleted_users.resource_path.segment, "microsoft.graph.user")

    def test4_get_deleted_applications(self):
        deleted_apps = self.client.directory.deleted_applications.get().execute_query()
        self.assertEqual(
            deleted_apps.resource_path.segment, "microsoft.graph.application"
        )

    def test5_get_member_objects(self):
        result = self.client.me.get_member_objects().execute_query()
        self.assertIsInstance(result.value, ClientValueCollection)

    def test6_list_directory_roles(self):
        result = self.client.directory_roles.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test7_create_administrative_unit(self):
    #    name = "Seattle District Technical Schools"
    #    result = self.client.directory.administrative_units.add(displayName=name).execute_query()
    #    self.assertIsNotNone(result.resource_path)
    #    self.__class__.administrative_unit = result

    def test8_list_administrative_units(self):
        result = self.client.directory.administrative_units.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test9_delete_administrative_unit(self):
    #    self.__class__.administrative_unit.delete_object().execute_query()

    def test9_list_directory_role_templates(self):
        result = self.client.directory_role_templates.get().execute_query()
        self.assertIsNotNone(result.resource_path)
