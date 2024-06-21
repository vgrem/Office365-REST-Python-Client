"""
Returns a SharePoint site status
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_admin_site_url, test_admin_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
result = admin_client.site_manager.get_status(test_team_site_url).execute_query()
print(result.value)
