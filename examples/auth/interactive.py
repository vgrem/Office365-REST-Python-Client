"""
Demonstrates how to login when the user may be prompted for input by the authorization server.
For example, to sign in, perform multi-factor authentication (MFA), or to grant consent
to more resource access permissions.

Note:
    in AAD portal ensure Mobile and Desktop application is added for application
    and http://localhost is set as redirect uri

https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-authentication-flows#interactive-and-non-interactive-authentication
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_tenant

client = GraphClient(tenant=test_tenant).with_token_interactive(test_client_id)
me = client.me.get().execute_query()
print("Welcome,  {0}!".format(me.given_name))
site = client.sites.root.get().execute_query()
print("Site Url:  {0}".format(site.web_url))
