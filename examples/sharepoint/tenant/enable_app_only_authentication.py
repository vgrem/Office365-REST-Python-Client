"""
Since for new tenants, apps using an ACS app-only access token is disabled by default,
you can change the behavior using the below script
https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs
"""


from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url

admin_client = ClientContext(test_admin_site_url).with_credentials(
    test_admin_credentials
)
if admin_client.tenant.get_property("DisableCustomAppAuthentication"):
    print("Enabling ACS app-only access token auth on tenant...")
    admin_client.tenant.set_property(
        "DisableCustomAppAuthentication", False
    ).update().execute_query()
    print("Done")
else:
    print("ACS app-only access token auth has been already enabled on tenant")
