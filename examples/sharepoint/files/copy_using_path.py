"""
Demonstrates how to copy a file within a site
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

file_from = ctx.web.get_file_by_server_relative_path(
    "Shared Documents/Financial Sample.xlsx"
)

folder_to = ctx.web.get_folder_by_server_relative_path("Shared Documents/archive")
file_to = file_from.copyto_using_path(folder_to, True).execute_query()
print("File has been copied into '{0}'".format(file_to.server_relative_path))
