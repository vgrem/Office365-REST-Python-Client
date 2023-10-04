import json

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
result = ctx.group_site_manager.get_current_user_joined_teams().execute_query()
data = json.loads(result.value)
for item in data["value"]:
    print(item["displayName"])
