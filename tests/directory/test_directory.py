from office365.runtime.client_value_collection import ClientValueCollection
from tests.graph_case import GraphTestCase


class TestDirectory(GraphTestCase):

    def test2_get_deleted_groups(self):
        deleted_groups = self.client.directory.deleted_groups.get().execute_query()
        self.assertEqual(deleted_groups.resource_path.key, 'microsoft.graph.group')

    def test3_get_deleted_users(self):
        deleted_users = self.client.directory.deleted_users.get().execute_query()
        self.assertEqual(deleted_users.resource_path.key, 'microsoft.graph.user')

    def test4_get_deleted_applications(self):
        deleted_apps = self.client.directory.deleted_applications.get().execute_query()
        self.assertEqual(deleted_apps.resource_path.key, 'microsoft.graph.application')

    def test5_get_member_objects(self):
        result = self.client.me.get_member_objects().execute_query()
        self.assertIsInstance(result.value, ClientValueCollection)

    def test6_list_directory_roles(self):
        result = self.client.directory_roles.get().execute_query()
        self.assertIsNotNone(result.resource_path)
