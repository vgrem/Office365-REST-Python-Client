"""
Demonstrates how to move a folder within a site
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.move_operations import MoveOperations
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)


file_from = ctx.web.get_file_by_server_relative_path(
    "Shared Documents/Financial Sample.xlsx"
)

# folder_to = ctx.web.get_folder_by_server_relative_url("Shared Documents")
folder_to = "Shared Documents/Archive"

file_to = file_from.move_to_using_path(
    folder_to, MoveOperations.overwrite
).execute_query()
print("'{0}' moved into '{1}'".format(file_from, file_to.server_relative_path))
