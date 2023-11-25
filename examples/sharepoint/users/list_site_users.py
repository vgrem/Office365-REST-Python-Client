"""
Retrieves site users
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
users = ctx.web.site_users.select(["LoginName"]).get().top(100).execute_query()
for user in users:
    print(user.login_name)
