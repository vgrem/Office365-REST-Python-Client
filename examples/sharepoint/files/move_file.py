"""
Demonstrates how to move a folder within a site
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.move_operations import MoveOperations
from tests import test_user_credentials, test_team_site_url, create_unique_name

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

print("Creating and uploading into it a temporary file...")
path = "../../data/report #123.csv"
root_folder = ctx.web.default_document_library().root_folder
folder_name = create_unique_name("Temp folder")
file = root_folder.add(folder_name).files.upload(path).execute_query()

# copies the file with a new name into folder
print("Moving file to parent folder...")
file_to = file.move_to_using_path("report moved.csv", MoveOperations.overwrite).execute_query()
print("File has been copied from '{0}' into '{1}'".format(file.server_relative_path, file_to.server_relative_path))

print("Cleaning up...")
file_to.delete_object().execute_query()
file.parent_folder.delete_object().execute_query()
