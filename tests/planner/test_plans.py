from tests.graph_case import GraphTestCase


class TestPlanner(GraphTestCase):
    target_group = None  # type: Group
    target_plan = None  # type: PlannerPlan

    @classmethod
    def setUpClass(cls):
        super(TestPlanner, cls).setUpClass()
        # Ensure Group for a Planner
        filter_str = "groupTypes/any(a:a eq 'unified')"
        groups = cls.client.groups.filter(filter_str).get().execute_query()
        cls.target_group = groups[0]
        cls.assertIsNotNone(cls.target_group.resource_path, "Group not found!")

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_create_plan(self):
        # plan_name = create_unique_name("My Plan")
        # new_plan = self.target_group.planner.plans.add(plan_name, self.client.me).execute_query()
        # self.assertIsNotNone(new_plan.id)
        # self.__class__.target_plan = new_plan
        pass

    def test2_list_my_plans(self):
        my_plans = self.client.me.planner.plans.get().execute_query()
        self.assertIsNotNone(my_plans.resource_path)
        self.assertGreaterEqual(len(my_plans), 0)

    def test3_delete_plan(self):
        # plan_to_del = self.__class__.target_plan
        # plan_to_del.delete_object().execute_query()
        pass
