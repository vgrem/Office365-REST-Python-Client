"""
Demonstrates how to authenticate users on devices or operating systems that don't provide a web browser.
Device code flow lets the user use another device such as a computer or a mobile phone to sign in interactively.

https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_tenant, test_client_id, test_site_url

ctx = ClientContext(test_site_url).with_device_flow(test_tenant, test_client_id)
me = ctx.web.current_user.get().execute_query()
print(me.login_name)
web = ctx.web.get().execute_query()
print(web.title)
