"""
Get folder at the specified path
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folder = ctx.web.folders.get_by_path("Shared Documents").get().execute_query()
print(folder)
