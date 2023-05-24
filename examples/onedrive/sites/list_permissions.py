"""
List site permissions
https://learn.microsoft.com/en-us/graph/api/site-list-permissions?view=graph-rest-1.0&tabs=http
"""
import json

from office365.graph_client import GraphClient
from tests import test_team_site_url
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
permissions = client.sites.get_by_url(test_team_site_url).permissions.get().execute_query()
print(json.dumps(permissions.to_json(), indent=4))
