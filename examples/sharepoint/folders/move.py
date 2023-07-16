"""
Demonstrates how to move a folder within a site
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url, create_unique_name

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)


print("Creating a temporary folders in a Documents library ...")
folder_from = ctx.web.default_document_library().root_folder.add(create_unique_name("in"))
folder_to_parent = ctx.web.default_document_library().root_folder.add(create_unique_name("out"))
# folder_to_url = "Shared Documents/archive"

print("Moving folder...")
#folder_to = folder_from.move_to_using_path(folder_to_parent).execute_query()
folder_to = folder_from.move_to(folder_to_parent).execute_query()
print("Folder has been moved into '{0}'".format(folder_to.serverRelativeUrl))

print("Cleaning up temporary folders ...")
folder_to_parent.delete_object().execute_query()
print("Done")
