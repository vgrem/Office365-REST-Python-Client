"""
Gets folder properties
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folder = (
    ctx.web.get_folder_by_server_relative_url("Shared Documents").get().execute_query()
)
print(folder.name)
