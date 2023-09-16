from tests.graph_case import GraphTestCase


class TestAzureADReports(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestAzureADReports, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_list_user_registration_details(self):
        result = self.client.reports.authentication_methods.user_registration_details.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_list_users_registered_by_method(self):
        result = self.client.reports.authentication_methods.users_registered_by_method().execute_query()
        self.assertIsNotNone(result.value)


