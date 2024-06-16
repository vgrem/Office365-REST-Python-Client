"""
Demonstrates how to copy a file within a site
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

file_from = ctx.web.get_file_by_server_relative_url(
    "Shared Documents/Financial Sample.xlsx"
)
folder_to = ctx.web.get_folder_by_server_relative_url("Shared Documents/archive")
# folder_to = "Shared Documents/archive/2002/02"
file_to = file_from.copyto(folder_to, True).execute_query()
print("{0} copied into '{1}'".format(file_from, file_to))
