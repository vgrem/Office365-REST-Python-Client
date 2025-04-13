from tests.graph_case import GraphTestCase


class TestInsights(GraphTestCase):


    def test1_list_trending(self):
        result = self.client.me.insights.trending.get().execute_query()
        self.assertIsNotNone(result.resource_path)
