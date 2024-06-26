"""
Connect via national clouds (Microsoft 365 GCC High environment)

Microsoft Graph for US Government L4: https://graph.microsoft.us
"""

import msal

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
    test_user_principal_name,
)


def acquire_token():
    authority_url = "https://login.microsoftonline.us/{0}".format(test_tenant)

    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=test_client_id,
        client_credential=test_client_secret,
    )
    return app.acquire_token_for_client(scopes=["https://graph.microsoft.us/.default"])


def construct_request(request):
    request.url = request.url.replace(
        "https://graph.microsoft.com", "https://graph.microsoft.us"
    )


client = GraphClient(acquire_token)
client.pending_request().beforeExecute += construct_request
messages = client.users[test_user_principal_name].messages.get().execute_query()
