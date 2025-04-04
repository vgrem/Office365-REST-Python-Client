"""
Acquires a token by using application secret

The following options are supported:
   - utilize built in GraphClient(tenant=tenant).with_client_secret(client_id, client_secret) method
   - or provide a custom callback function to GraphClient constructor as demonstrated below

https://learn.microsoft.com/en-us/entra/identity-platform/msal-authentication-flows#client-credentials
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
root_site = client.sites.root.get().execute_query()
print(root_site.web_url)
