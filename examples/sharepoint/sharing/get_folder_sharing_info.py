from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

folder_url = "/sites/team/Shared Documents/Archive"
result = ctx.web.get_folder_by_server_relative_url(folder_url).get_sharing_information().execute_query()
print(result.properties)

