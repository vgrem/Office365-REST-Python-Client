"""
Demonstrates how to copy a folder within a site
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url, create_unique_name

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

# creates a temporary folder first in a Documents library
folder_from = ctx.web.default_document_library().root_folder.add(create_unique_name("from"))
folder_to = ctx.web.default_document_library().root_folder.add(create_unique_name("to"))

# copies the folder with a new name
folder = folder_from.copy_to_using_path(folder_to).execute_query()
print("Folder has been copied from '{0}' into '{1}'".format(folder_from.serverRelativeUrl, folder.serverRelativeUrl))

# clean up
folder_from.delete_object().execute_query()
folder_to.delete_object().execute_query()
