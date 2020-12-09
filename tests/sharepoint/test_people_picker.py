from office365.sharepoint.ui.applicationpages.clientPeoplePickerQueryParameters import ClientPeoplePickerQueryParameters
from office365.sharepoint.ui.applicationpages.clientPeoplePickerWebServiceInterface import \
    ClientPeoplePickerWebServiceInterface
from settings import settings
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPPeoplePicker(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSPPeoplePicker, cls).setUpClass()

    def test1_get_search_results(self):
        params = ClientPeoplePickerQueryParameters(settings.get('first_account_name'))
        result = ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(self.client, params)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    # def test2_get_search_results(self):
    #    result = ClientPeoplePickerWebServiceInterface.get_search_results(self.client, "mdoe")
    #    self.client.execute_query()
    #    self.assertIsNotNone(result.value)
