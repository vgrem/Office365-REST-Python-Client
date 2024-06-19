"""
Gets information about all hub sites that the current user can access.
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
hub_sites = ctx.hub_sites.get().execute_query()
for hub_site in hub_sites:
    print(hub_site)
