from tests.graph_case import GraphTestCase


class TestServicePrincipal(GraphTestCase):

    def test1_list_service_principals(self):
        principals = self.client.service_principals.get().execute_query()
        self.assertIsNotNone(principals.resource_path)
