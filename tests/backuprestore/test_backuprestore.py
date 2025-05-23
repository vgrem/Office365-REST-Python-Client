from tests.graph_case import GraphTestCase


class TestBackupRestore(GraphTestCase):

    def test1_enable_backup_restore(self):
        tenant_id = "af6a80a4-8b4b-4879-88af-42ff8a545211"
        result = self.client.solutions.backup_restore.enable(tenant_id).execute_query()
        self.assertIsNotNone(result.value)

    def test2_get_backup_restore(self):
        result = self.client.solutions.backup_restore.get().execute_query()
        self.assertIsNotNone(result.resource_path)
