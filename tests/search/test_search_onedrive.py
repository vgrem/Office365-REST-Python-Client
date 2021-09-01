from tests.graph_case import GraphTestCase


class TestSearchOneDrive(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSearchOneDrive, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_search_files(self):
        result = self.client.search.query("Guide.docx", entity_types=["driveItem"]).execute_query()
        self.assertIsNotNone(result.value)

