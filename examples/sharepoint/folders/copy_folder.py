from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

source_folder_url = "/sites/team/Shared Documents/Archive/2020"
target_folder_url = "/sites/team/Shared Documents/Archive/2020/01"

source_folder = ctx.web.get_folder_by_server_relative_url(source_folder_url)
target_folder = source_folder.copy_to_using_path(target_folder_url, True).get().execute_query()
# MoveCopyUtil.copy_folder(ctx, source_folder_url, target_folder_url).execute_query()
#print(f"File copied into {target_folder.serverRelativeUrl}")
