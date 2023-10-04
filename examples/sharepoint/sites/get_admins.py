"""

"""
import json

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
result = client.site.get_site_administrators().execute_query()
print(json.dumps(result.value.to_json(), indent=4))
