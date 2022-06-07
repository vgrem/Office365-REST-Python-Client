import json

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
site_users = ctx.web.site_users.get().execute_query()
json_data = [u.login_name for u in site_users]
print(json.dumps(json_data, indent=4))
