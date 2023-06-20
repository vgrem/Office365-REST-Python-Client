"""
Demonstrates how to copy a folder within a site
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url, create_unique_name

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

# creates a temporary folder first in a Documents library
folder_name = create_unique_name("New folder")
folder_from = ctx.web.default_document_library().root_folder.add(folder_name)

# copies the folder with a new name
new_folder_name = create_unique_name("Copied folder")
folder_to = folder_from.copy_to(new_folder_name).execute_query()
print("Folder has been copied from '{0}' into '{1}'".format(folder_from.serverRelativeUrl, folder_to.serverRelativeUrl))

# clean up
folder_from.delete_object().execute_query()
folder_to.delete_object().execute_query()
