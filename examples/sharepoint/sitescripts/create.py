import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sitescripts.utility import SiteScriptUtility
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

# The following example creates a new site script that applies a custom theme.

site_script = {
    "$schema": "schema.json",
    "actions": [{"verb": "applyTheme", "themeName": "Contoso Theme"}],
    "bindata": {},
    "version": 1,
}

result = SiteScriptUtility.create_site_script(
    ctx, "Contoso theme script", "", site_script
).execute_query()
print(json.dumps(result.value.to_json(), indent=4))
