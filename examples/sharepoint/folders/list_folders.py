"""
Demonstrates how to retrieve folders
If 'recursive' flag set to True, it traverses all sub folders
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folders = (
    ctx.web.default_document_library().root_folder.get_folders(False).execute_query()
)
for folder in folders:
    print(
        "Url: {0}, Created: {1}".format(folder.serverRelativeUrl, folder.time_created)
    )
