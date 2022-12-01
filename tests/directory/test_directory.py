from office365.runtime.client_value_collection import ClientValueCollection
from tests.graph_case import GraphTestCase


class TestDirectory(GraphTestCase):

    def test1_get_deleted_groups(self):
        deleted_groups = self.client.directory.deleted_groups.get().execute_query()
        self.assertEqual(deleted_groups.resource_path.name, 'microsoft.graph.group')

    def test2_get_deleted_users(self):
        deleted_users = self.client.directory.deleted_users.get().execute_query()
        self.assertEqual(deleted_users.resource_path.name, 'microsoft.graph.user')

    def test3_get_deleted_applications(self):
        deleted_apps = self.client.directory.deleted_applications.get().execute_query()
        self.assertEqual(deleted_apps.resource_path.name, 'microsoft.graph.application')

    def test4_get_member_objects(self):
        result = self.client.me.get_member_objects().execute_query()
        self.assertIsInstance(result.value, ClientValueCollection)

    def test5_list_directory_roles(self):
        result = self.client.directory_roles.get().execute_query()
        self.assertIsNotNone(result.resource_path)
