"""
Acquires a token by using application secret

The following options are supported:
   - utilize built in GraphClient(tenant=tenant).with_client_secret(client_id, client_secret) method
   - or provide a custom callback function to GraphClient constructor as demonstrated below

https://learn.microsoft.com/en-us/entra/identity-platform/msal-authentication-flows#client-credentials
"""

import msal

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant


def acquire_token():
    authority_url = "https://login.microsoftonline.com/{0}".format(test_tenant)
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=test_client_id,
        client_credential=test_client_secret,
    )
    return app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])


client = GraphClient(acquire_token)
root_site = client.sites.root.get().execute_query()
print(root_site.web_url)
