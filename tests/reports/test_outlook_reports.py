from tests.graph_case import GraphTestCase


class TestOutlookReports(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestOutlookReports, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_email_activity_counts(self):
        result = self.client.reports.get_email_activity_counts("D7").execute_query()
        self.assertIsNotNone(result.value)

    def test2_get_m365_app_user_counts(self):
        result = self.client.reports.get_m365_app_user_counts("D7").execute_query()
        self.assertIsNotNone(result.value)


