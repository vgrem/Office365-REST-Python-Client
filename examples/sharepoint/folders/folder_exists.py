"""
 How to determine whether folder exist?
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folder_path = "Shared Documents"
folder = (
    ctx.web.get_folder_by_server_relative_url(folder_path)
    .select(["Exists"])
    .get()
    .execute_query()
)
if folder.exists:
    print("Folder '{0}' is found".format(folder_path))
else:
    print("Folder '{0}' not found".format(folder_path))
