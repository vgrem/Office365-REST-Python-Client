from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

target_folder_url = "/Shared Documents/Archive/2020/09"
target_folder_url = ctx.web.ensure_folder_path(target_folder_url).execute_query()
print(target_folder_url.serverRelativeUrl)





