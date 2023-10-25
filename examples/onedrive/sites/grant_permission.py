"""
Grant permissions on a site.

https://learn.microsoft.com/en-us/graph/api/site-post-permissions?view=graph-rest-1.0
"""
import json

from office365.graph_client import GraphClient
from tests import test_client_credentials, test_team_site_url
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)

print("Retrieving app...")
app = client.applications.get_by_app_id(test_client_credentials.clientId)

print("Granting an Application a permissions on Site...")
site = client.sites.get_by_url(test_team_site_url)
permission = site.permissions.add(["read", "write"], app).execute_query()
print(json.dumps(permission.granted_to.to_json(), indent=4))
