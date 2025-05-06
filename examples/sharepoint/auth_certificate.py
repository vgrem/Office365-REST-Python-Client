"""
When using SharePoint Online you can define applications in Azure AD and these applications can
be granted permissions to SharePoint, but also to all the other services in Office 365.
This model is the preferred model in case you're using SharePoint Online, if you're using SharePoint on-premises
you have to use the SharePoint Only model via based Azure ACS as described in here:

Demonstrates how to use Azure AD App-Only auth flow

https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread

Refer wiki for a more details:
https://github.com/vgrem/Office365-REST-Python-Client/wiki/
How-to-connect-to-SharePoint-Online-with-certificate-credentials
"""

from office365.sharepoint.client_context import ClientContext
from tests import (
    test_cert_thumbprint,
    test_client_id,
    test_site_url,
    test_tenant,
)

cert_credentials = {
    "tenant": test_tenant,
    "client_id": test_client_id,
    "thumbprint": test_cert_thumbprint,
    "cert_path": "./selfsigncert.pem",
}
ctx = ClientContext(test_site_url).with_client_certificate(**cert_credentials)
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
