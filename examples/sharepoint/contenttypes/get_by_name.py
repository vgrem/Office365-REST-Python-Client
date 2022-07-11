import json

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
ct = ctx.web.content_types.get_by_name("Document").get().execute_query()
print(json.dumps(ct.to_json(), indent=4))
