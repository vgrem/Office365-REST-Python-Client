import json

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
users = ctx.web.site_users.select(["LoginName"]).get().execute_query()
print(json.dumps(users.to_json(), indent=4))
