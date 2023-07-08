"""
Demonstrates how to acquire a token by using certificate credentials.

https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-authentication-flows#certificates
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_tenant_name, test_cert_path, test_cert_thumbprint


def acquire_token():
    with open(test_cert_path, 'r') as f:
        private_key = open(test_cert_path).read()

    authority_url = 'https://login.microsoftonline.com/{0}'.format(test_tenant_name)
    credentials = {"thumbprint": test_cert_thumbprint, "private_key": private_key}
    import msal
    app = msal.ConfidentialClientApplication(
        test_client_id,
        authority=authority_url,
        client_credential=credentials,
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result


client = GraphClient(acquire_token)
drives = client.drives.get().top(10).execute_query()
for drive in drives:
    print(drive.web_url)
