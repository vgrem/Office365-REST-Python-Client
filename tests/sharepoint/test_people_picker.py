from office365.sharepoint.ui.applicationpages.peoplepicker.web_service_interface import \
    ClientPeoplePickerWebServiceInterface
from tests import test_user_principal_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPPeoplePicker(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSPPeoplePicker, cls).setUpClass()

    def test1_get_search_results(self):
        result = ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(self.client,
                                                                                         test_user_principal_name)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    #def test2_get_picker_entity_information(self):
    #    result = ClientPeoplePickerWebServiceInterface.get_picker_entity_information(self.client,
    #                                                                                 test_user_principal_name)
    #    self.client.execute_query()
    #    self.assertIsNotNone(result.value)

    # def test2_get_search_results(self):
    #    result = ClientPeoplePickerWebServiceInterface.get_search_results(self.client, "mdoe")
    #    self.client.execute_query()
    #    self.assertIsNotNone(result.value)

    #def test3_get_search_results(self):
    #    result = ClientPeoplePickerWebServiceInterface.get_search_results(self.client, "John")
    #    self.client.execute_query()
    #    self.assertIsNotNone(result.value)

