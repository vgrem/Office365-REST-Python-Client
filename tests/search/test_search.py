from office365.search.entity_type import EntityType
from tests.graph_case import GraphTestCase


class TestSearchOneDrive(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSearchOneDrive, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_search_files(self):
        result = self.client.search.query(
            "Guide.docx", entity_types=[EntityType.driveItem]
        ).execute_query()
        self.assertIsNotNone(result.value)

    def test2_search_messages(self):
        result = self.client.search.query_messages("Jon Doe").execute_query()
        self.assertIsNotNone(result.value)

    # def test3_search_events(self):
    #    result = self.client.search.query_events("Jon Doe").execute_query()
    #    self.assertIsNotNone(result.value)
