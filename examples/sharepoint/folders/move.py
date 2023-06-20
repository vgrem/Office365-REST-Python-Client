"""
Demonstrates how to move a folder within a site
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url, create_unique_name

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

folder_name = create_unique_name("New folder")
print("Creating a temporary folder in a Documents library ...")
folder_from = ctx.web.default_document_library().root_folder.add(folder_name).execute_query()
print("Folder '{0}' has been created".format(folder_from.serverRelativeUrl))

new_folder_name = create_unique_name("Moved folder")
print("Moving folder...")
folder_to = folder_from.move_to(new_folder_name).execute_query()
print("Folder has been moved from '{0}' into '{1}'".format(folder_from.serverRelativeUrl, folder_to.serverRelativeUrl))

print("Cleaning up temporary folders ...")
folder_from.delete_object().execute_query()
folder_to.delete_object().execute_query()
print("Done")
