"""
Demonstrates how to create a folder with a color
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.folders.coloring_information import FolderColors
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)


root_folder = ctx.web.default_document_library().root_folder
folder = root_folder.folders.add(
    "Report123", color_hex=FolderColors.DarkGreen
).execute_query()
print("Folder : {0} has been created".format(folder.serverRelativeUrl))
