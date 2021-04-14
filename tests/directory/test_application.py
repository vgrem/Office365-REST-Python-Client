from tests.graph_case import GraphTestCase


class TestApplication(GraphTestCase):

    def test1_list_apps(self):
        apps = self.client.applications.get().execute_query()
        self.assertIsNotNone(apps.resource_path)
