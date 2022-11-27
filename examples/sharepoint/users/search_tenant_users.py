import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.ui.applicationpages.peoplepicker.web_service_interface import \
    ClientPeoplePickerWebServiceInterface
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
result = ClientPeoplePickerWebServiceInterface.client_people_picker_search_user(ctx, "Doe").execute_query()
entries = json.loads(result.value)
for entry in entries:
    print(entry.get('DisplayText', None))
