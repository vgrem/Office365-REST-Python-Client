from office365.sharepoint.ui.applicationpages.client_people_picker import \
    ClientPeoplePickerWebServiceInterface, ClientPeoplePickerQueryParameters
from tests import test_user_principal_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPPeoplePicker(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSPPeoplePicker, cls).setUpClass()

    def test1_get_search_results(self):
        params = ClientPeoplePickerQueryParameters(test_user_principal_name)
        result = ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(self.client, params)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    # def test2_get_search_results(self):
    #    request = PickerEntityInformationRequest(Key=settings.get('first_account_name'), GroupId=-1)
    #    result = ClientPeoplePickerWebServiceInterface.get_picker_entity_information(self.client, request)
    #    self.client.execute_query()
    #    self.assertIsNotNone(result.value)

    # def test2_get_search_results(self):
    #    result = ClientPeoplePickerWebServiceInterface.get_search_results(self.client, "mdoe")
    #    self.client.execute_query()
    #    self.assertIsNotNone(result.value)
