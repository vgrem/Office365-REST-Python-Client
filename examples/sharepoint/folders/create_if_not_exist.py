"""
Returns a folder from a given site relative path, and will create it if it does not exist
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
folder_url = "Shared Documents/Archive/2023/10/1"
folder = (
    ctx.web.ensure_folder_path(folder_url)
    .get()
    .select(["ServerRelativePath"])
    .execute_query()
)
print(folder.server_relative_path)
