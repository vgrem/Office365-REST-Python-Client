"""
Demonstrates how to move a folder within a site
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.move_operations import MoveOperations
from tests import test_user_credentials, test_team_site_url, create_unique_name

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

print("Creating temporary folders and uploading a file...")
path = "../../data/report #123.csv"
folder_from = ctx.web.default_document_library().root_folder.add(create_unique_name("from"))
folder_to = ctx.web.default_document_library().root_folder.add(create_unique_name("to"))
file = folder_from.files.upload(path).execute_query()

# copies the file with a new name into folder
print("Moving file to parent folder...")
file_to = file.move_to_using_path(folder_to, MoveOperations.overwrite).execute_query()
print("File has been copied from '{0}' into '{1}'".format(file.server_relative_path, folder_to.serverRelativeUrl))

print("Cleaning up...")
folder_from.delete_object().execute_query()
folder_to.delete_object().execute_query()
