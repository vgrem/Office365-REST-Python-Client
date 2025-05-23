"""
Demonstrates how to acquire access token via ADAL library

Note: ADAL for Python is no longer receive new feature improvement. Its successor, MSAL for Python,
are now generally available.
"""

from office365.graph_client import GraphClient
from tests import test_tenant_name, test_client_id, test_username, test_password


def acquire_token():
    import adal  # pylint: disable=E0401

    authority_url = "https://login.microsoftonline.com/{0}".format(test_tenant_name)
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_username_password(
        "https://graph.microsoft.com",
        test_username,
        test_password,
        test_client_id,
    )
    return token


client = GraphClient(acquire_token)
me = client.me.get().execute_query()
print(me.properties("displayName"))
