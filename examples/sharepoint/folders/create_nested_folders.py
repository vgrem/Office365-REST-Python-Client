from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])
ctx = ClientContext(settings['team_site_url']).with_credentials(credentials)

target_folder_url = "/Shared Documents/Archive/2020/09"
target_folder_url = ctx.web.ensure_folder_path(target_folder_url).execute_query()
print(target_folder_url.serverRelativeUrl)





