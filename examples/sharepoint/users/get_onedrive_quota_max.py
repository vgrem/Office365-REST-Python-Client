"""
Get OneDrive quota max for a user
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_password, test_site_url, test_username

ctx = ClientContext(test_site_url).with_user_credentials(test_username, test_password)
result = ctx.people_manager.get_user_onedrive_quota_max(test_username).execute_query()
print(result.value)
