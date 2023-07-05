"""
Demonstrates how to acquire a token by using certificate credentials.

https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-authentication-flows#certificates
"""

from examples import sample_tenant_name, sample_thumbprint, sample_cert_path
from office365.graph_client import GraphClient
from tests import test_client_id


def acquire_token():
    with open(sample_cert_path, 'r') as f:
        private_key = open(sample_cert_path).read()

    authority_url = 'https://login.microsoftonline.com/{0}'.format(sample_tenant_name)
    credentials = {"thumbprint": sample_thumbprint, "private_key": private_key}
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
