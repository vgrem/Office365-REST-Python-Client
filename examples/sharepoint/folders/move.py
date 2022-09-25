from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

source_folder_url = "/sites/team/Shared Documents/2021"
target_folder_url = "/sites/team/Shared Documents/2022"
source_folder = ctx.web.get_folder_by_server_relative_url(source_folder_url)
source_folder.move_to(target_folder_url).execute_query()
