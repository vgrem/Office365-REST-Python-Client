import json

from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
hub_sites = ctx.hub_sites.get().execute_query()
print(json.dumps(hub_sites.to_json(), indent=4))
