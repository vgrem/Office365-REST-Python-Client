from tests.graph_case import GraphTestCase


class TestDirectory(GraphTestCase):

    def test1_get_deleted_groups(self):
        deleted_groups = self.client.directory.deletedGroups.get().execute_query()
        self.assertEqual(deleted_groups.resource_path.segment, 'microsoft.graph.group')

    def test2_get_deleted_users(self):
        deleted_users = self.client.directory.deletedUsers.get().execute_query()
        self.assertEqual(deleted_users.resource_path.segment, 'microsoft.graph.user')

    def test3_get_deleted_applications(self):
        deleted_apps = self.client.directory.deletedApplications.get().execute_query()
        self.assertEqual(deleted_apps.resource_path.segment, 'microsoft.graph.application')
