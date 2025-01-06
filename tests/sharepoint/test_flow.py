from tests.sharepoint.sharepoint_case import SPTestCase


class TestFlow(SPTestCase):

    def test_1_get_flow_permission_level(self):
        lib = self.client.web.default_document_library()
        result = lib.get_flow_permission_level().execute_query()
        self.assertIsNotNone(result.value)
