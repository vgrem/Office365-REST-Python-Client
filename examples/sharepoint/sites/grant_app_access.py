"""
Controlling app access on a specific SharePoint site collection

Refer:
https://developer.microsoft.com/en-us/office/blogs/controlling-app-access-on-specific-sharepoint-site-collections/
"""

from office365.graph_client import GraphClient
from tests import test_client_credentials, test_team_site_url
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
site = client.sites.get_by_url(test_team_site_url)
app = client.applications.get_by_app_id(test_client_credentials.clientId)
roles = ["read", "write"]

print("Granting {0} permissions for application {1}".format(roles, app))
site.permissions.add(roles, app).execute_query()
result = site.permissions.get().execute_query()
for perm in result:
    print("Current permissions: {0}".format(perm.granted_to_identities))
