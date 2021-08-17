from tests.graph_case import GraphTestCase


class TestPlanner(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPlanner, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test2_list_my_plans(self):
        my_plans = self.client.me.planner.plans.get().execute_query()
        self.assertIsNotNone(my_plans.resource_path)

