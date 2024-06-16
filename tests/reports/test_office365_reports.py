from tests.graph_case import GraphTestCase


class TestOffice365Reports(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestOffice365Reports, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_office365_activations_user_counts(self):
        result = (
            self.client.reports.get_office365_activations_user_counts().execute_query()
        )
        self.assertIsNotNone(result.value)
