"""
Retrieves authorization related settings across the company

https://learn.microsoft.com/en-us/graph/api/authorizationpolicy-get?view=graph-rest-1.0

"""
from pprint import pprint

from office365.graph_client import GraphClient
from tests import test_admin_principal_name, test_client_id, test_tenant

client = GraphClient.with_token_interactive(
    test_tenant, test_client_id, test_admin_principal_name
)


result = client.policies.authorization_policy.get().execute_query()
pprint(result.to_json())
