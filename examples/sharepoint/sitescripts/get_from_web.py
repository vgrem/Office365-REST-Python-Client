from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
# This example creates the site script output from an existing site
result = ctx.web.get_site_script(included_lists=["Shared Documents"]).execute_query()
print(result.value.JSON)
