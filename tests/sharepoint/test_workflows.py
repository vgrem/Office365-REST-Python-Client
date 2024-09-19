from tests.sharepoint.sharepoint_case import SPTestCase


class TestWorkflows(SPTestCase):
    def test1_get_manager(self):
        manager = self.client.workflow_services_manager.get().execute_query()
        self.assertIsNotNone(manager.resource_path)

    # def test2_enumerate_definitions(self):
    #    manager = self.client.workflow_deployment_service.enumerate_definitions().execute_query()
    #    self.assertIsNotNone(manager.resource_path)
