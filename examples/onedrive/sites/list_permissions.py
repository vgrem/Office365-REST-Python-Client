"""
List site permissions
https://learn.microsoft.com/en-us/graph/api/site-list-permissions?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_team_site_url, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
permissions = (
    client.sites.get_by_url(test_team_site_url).permissions.get().execute_query()
)
for perm in permissions:
    print("Roles: {0}, Granted to: {1}".format(perm.roles, perm.granted_to))
