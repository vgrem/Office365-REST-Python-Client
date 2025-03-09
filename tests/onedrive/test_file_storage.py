from tests.graph_case import GraphTestCase


class TestFileStorage(GraphTestCase):
    """File storage test case base class"""

    def test1_list_containers(self):
        result = self.client.storage.file_storage.containers.get().execute_query()
        self.assertIsNotNone(result.resource_path)
