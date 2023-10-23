"""
List the directory roles that are activated in the tenant.

https://learn.microsoft.com/en-us/graph/api/directoryrole-list?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
roles = client.directory_roles.get().execute_query()
for role in roles:
    print(role)
