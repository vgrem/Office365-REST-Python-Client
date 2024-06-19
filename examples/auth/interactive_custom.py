"""
Demonstrates how to login when the user may be prompted for input by the authorization server.
For example, to sign in, perform multi-factor authentication (MFA), or to grant consent
to more resource access permissions.

Note:
    in AAD portal ensure Mobile and Desktop application is added for application
    and http://localhost is set as redirect uri

https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-authentication-flows#interactive-and-non-interactive-authentication
"""

import msal

from office365.graph_client import GraphClient
from tests import test_client_id, test_tenant


def acquire_token():
    app = msal.PublicClientApplication(
        test_client_id,
        authority="https://login.microsoftonline.com/{0}".format(test_tenant),
        client_credential=None,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_interactive(scopes=scopes)
    return result


client = GraphClient(acquire_token)
me = client.me.get().execute_query()
print(me.user_principal_name)
