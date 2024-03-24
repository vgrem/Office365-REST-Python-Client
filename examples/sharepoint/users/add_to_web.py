"""

If the specified login name belongs to a valid user of the site, returns the User object corresponding to that user.

If the specified login name belongs to a valid user outside of the site, adds the user to the site and
returns the User object corresponding to that user.

"""
from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_team_site_url, test_user_principal_name

client = ClientContext(test_team_site_url).with_credentials(test_admin_credentials)
target_user = client.web.ensure_user(test_user_principal_name).execute_query()
print(target_user)
