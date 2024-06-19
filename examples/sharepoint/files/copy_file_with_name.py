"""
Demonstrates how to copy a file within a site
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

file_from = ctx.web.get_file_by_server_relative_url(
    "Shared Documents/Financial Sample.xlsx"
)
folder_to_url = "Shared Documents/archive"
new_filename = "Financial 2023.xlsx"
file_to = file_from.copyto(folder_to_url, True, new_filename).execute_query()
print("File copied into '{0}'".format(file_to.serverRelativeUrl))
