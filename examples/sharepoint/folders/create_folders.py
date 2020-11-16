from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])
ctx = ClientContext(settings['url']).with_credentials(credentials)

# create one folder only
target_folder = "/Shared Documents/test_folder"
target_folder = ctx.web.get_folder_by_server_relative_url(target_folder)
target_folder.add("new_folder")
ctx.execute_query()  # have to execute

# create relative folder tree, no execution required
target_folder = "/Shared Documents/test_folder/20201116/1133/test"
target_folder = ctx.web.create_folder_tree(target_folder)





