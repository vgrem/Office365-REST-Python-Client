"""
Retrieves the current user details
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
whoami = ctx.web.current_user.get().execute_query()
print(whoami)
