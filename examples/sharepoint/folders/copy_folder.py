from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])
ctx = ClientContext(settings['url']).with_credentials(credentials)

source_folder_url = "/Shared Documents/Archive"
target_folder_url = "/Docs/Archive/2012"


source_folder = ctx.web.get_folder_by_server_relative_url(source_folder_url)
target_folder = source_folder.copy_to(target_folder_url).get().execute_query()
print(f"File copied into {target_folder.serverRelativeUrl}")

