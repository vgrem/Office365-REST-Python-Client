from tests import test_user_principal_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPPeoplePicker(SPTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSPPeoplePicker, cls).setUpClass()

    def test1_client_people_picker_resolve_user(self):
        result = (
            self.client.client_people_picker.client_people_picker_resolve_user(
                self.client, test_user_principal_name
            )
        ).execute_query()
        self.assertIsNotNone(result.value)

    # def test2_get_picker_entity_information(self):
    #    result = self.client.client_people_picker.get_picker_entity_information(self.client,
    #                                                                         test_user_principal_name).execute_query()
    #    self.assertIsNotNone(result.value)

    def test3_get_search_results(self):
        result = self.client.people_picker.get_search_results(
            self.client, "Doe"
        ).execute_query()
        self.assertIsNotNone(result.value)
