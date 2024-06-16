"""
Demonstrates how to login when the user may be prompted for input by the authorization server.
For example, to sign in, perform multi-factor authentication (MFA), or to grant consent
to more resource access permissions.

Prerequisite: In Azure Portal, configure the Redirect URI of your
        "Mobile and Desktop application" as ``http://localhost``.

https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-authentication-flows#interactive-and-non-interactive-authentication
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_id, test_site_url, test_tenant

ctx = ClientContext(test_site_url).with_interactive(test_tenant, test_client_id)
me = ctx.web.current_user.get().execute_query()
print(me)
web = ctx.web.get().execute_query()
print(web)
