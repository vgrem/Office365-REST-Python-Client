from tests.graph_case import GraphTestCase


class TestSearchOneDrive(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSearchOneDrive, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_search_files(self):
        result = self.client.search.query_drive_items("Guide.docx").execute_query()
        self.assertIsNotNone(result.value)

    def test2_search_messages(self):
        result = self.client.search.query_messages("Jon Doe").execute_query()
        self.assertIsNotNone(result.value)

    # def test3_search_events(self):
    #    result = self.client.search.query_events("Jon Doe").execute_query()
    #    self.assertIsNotNone(result.value)

    def test4_search_list_items(self):
        result = self.client.search.query_list_items("Guide").execute_query()
        self.assertIsNotNone(result.value)

    # def test5_search_people_by_name(self):
    #    result = self.client.search.query_peoples("John").execute_query()
    #    self.assertIsNotNone(result.value)

    def test6_search_sites(self):
        result = self.client.search.query_sites("team").execute_query()
        self.assertIsNotNone(result.value)
