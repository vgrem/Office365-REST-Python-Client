from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

source_folder_url = "/sites/team/Shared Documents/Archive2012"
target_folder_url = "/sites/team/Shared Documents/Archive2013"


source_folder = ctx.web.get_folder_by_server_relative_url(source_folder_url)
target_folder = source_folder.move_to_by_path(target_folder_url).get().execute_query()
print(f"File copied into {target_folder.server_relative_path.DecodedUrl}")

