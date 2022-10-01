from tests.sharepoint.sharepoint_case import SPTestCase


class TestViva(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestViva, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_app_configuration(self):
        return_type = self.client.ee.app_configuration.get().execute_query()
        self.assertIsNotNone(return_type.resource_path)


