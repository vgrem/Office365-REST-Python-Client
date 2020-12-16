from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])
ctx = ClientContext(settings['url']).with_credentials(credentials)

target_folder = "/Shared Documents/Archive/2020/Sept"
target_folder = ctx.web.ensure_folder_path(target_folder).execute_query()
print(target_folder.serverRelativeUrl)





