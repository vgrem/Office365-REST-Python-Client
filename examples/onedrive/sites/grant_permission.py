"""
Grants permissions on a site.

https://learn.microsoft.com/en-us/graph/api/site-post-permissions?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_team_site_url,
    test_tenant,
)

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)

print("Retrieving app...")
app = client.applications.get_by_app_id(test_client_id)

print("Granting an Application a permissions on Site...")
site = client.sites.get_by_url(test_team_site_url)
permission = site.permissions.add(["write"], app).execute_query()
print(permission.granted_to)
