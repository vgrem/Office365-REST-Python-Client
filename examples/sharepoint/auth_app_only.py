"""
There are two approaches for doing app-only for SharePoint:

   - Using an Azure AD application: this is the preferred method when using SharePoint Online because you can also
    grant permissions to other Office 365 services (if needed) + you’ve a user interface (Azure portal) to maintain
    your app principals.

   - Using a SharePoint App-Only principal: this method is older and only works for SharePoint access,
     but is still relevant. This method is also the recommended model when you’re still working in SharePoint
     on-premises since this model works in both SharePoint on-premises as SharePoint Online.

Important:
        Please safeguard the created client id/secret combination as would it be your administrator account.
        Using this client id/secret one can read/update all data in your SharePoint Online environment!

The example demonstrates how to use SharePoint App-Only principal (second option)

https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs

Notice:
Starting April 2, 2026, Azure Access Control service (ACS) usage will be retired for SharePoint in Microsoft 365
and users will no longer be able to create or use Azure ACS principals to access SharePoint.
Learn more about the [Access Control retirement](https://aka.ms/retirement/acs/support)
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_id, test_client_secret, test_site_url

ctx = ClientContext(test_site_url).with_client_credentials(
    test_client_id, test_client_secret
)
target_web = ctx.web.get().execute_query()
print(target_web.url)
