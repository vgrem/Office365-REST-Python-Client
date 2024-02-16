from tests.graph_case import GraphTestCase


class TestAuthentication(GraphTestCase):
    def test1_list_methods(self):
        result = self.client.me.authentication.methods.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test2_list_strength_policies(self):
    #    result = self.client.policies.authentication_strength_policies().get().execute_query()
    #    self.assertIsNotNone(result.resource_path)
