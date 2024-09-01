from tests.graph_case import GraphTestCase


class TestBackupRestore(GraphTestCase):

    def test1_get_backup_restore(self):
        result = self.client.solutions.backup_restore.get().execute_query()
        self.assertIsNotNone(result.resource_path)
