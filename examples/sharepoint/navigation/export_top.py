"""
Export the top navigation
"""
import json

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
nav = ctx.web.navigation.top_navigation_bar.get().execute_query()
print(json.dumps(nav.to_json(), indent=4))
