"""
Demonstrates how to login when the user may be prompted for input by the authorization server.
For example, to sign in, perform multi-factor authentication (MFA), or to grant consent
to more resource access permissions.

Prerequisite: In Azure Portal, configure the Redirect URI of your
        "Mobile and Desktop application" as ``http://localhost``.

https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-authentication-flows#interactive-and-non-interactive-authentication
"""

import msal

from office365.runtime.auth.token_response import TokenResponse
from office365.sharepoint.client_context import ClientContext
from tests import test_client_id, test_site_url, test_tenant, test_tenant_name


def acquire_token():
    app = msal.PublicClientApplication(
        test_client_id,
        authority="https://login.microsoftonline.com/{0}".format(test_tenant),
        client_credential=None,
    )
    scopes = ["https://{0}.sharepoint.com/.default".format(test_tenant_name)]
    result = app.acquire_token_interactive(scopes=scopes)
    return TokenResponse.from_json(result)


ctx = ClientContext(test_site_url).with_access_token(acquire_token)
me = ctx.web.current_user.get().execute_query()
web = ctx.web.get().execute_query()
print(me.login_name)
print(web.title)
