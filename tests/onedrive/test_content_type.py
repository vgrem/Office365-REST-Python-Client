from tests.graph_case import GraphTestCase


class TestContentType(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestContentType, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_compatible_hub_content_types(self):
        cts = self.client.sites.root.content_types.get_compatible_hub_content_types().execute_query()
        self.assertIsNotNone(cts.resource_path)

