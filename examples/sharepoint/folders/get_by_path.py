from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folder = ctx.web.folders.get_by_path('Shared Documents')
ctx.load(folder, ["ServerRelativeUrl", "Folders"]).execute_query()
print(folder.serverRelativeUrl)
