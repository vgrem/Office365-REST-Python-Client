"""
Prerequisites:

Setting up an Azure AD app for app-only access:

- create a self signed certificate
- register an Azure AD application in the Azure Active Directory tenant that is linked to your Office 365 tenant
- grant the permissions once application is registered, for instance choose:
      SharePoint
        Application permissions
          Sites
            Sites.FullControl.All
- and finally upload the certificate to the application

Refer this article for a detailed instruction:
https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread
"""

import os

from office365.sharepoint.client_context import ClientContext
from tests import test_cert_thumbprint, test_client_id, test_site_url, test_tenant

cert_path = "{0}/../selfsignkey.pem".format(os.path.dirname(__file__))
with open(cert_path, "r") as f:
    private_key = open(cert_path).read()

cert_credentials = {
    "tenant": test_tenant,
    "client_id": test_client_id,
    "thumbprint": test_cert_thumbprint,
    "private_key": private_key,
}
ctx = ClientContext(test_site_url).with_client_certificate(**cert_credentials)
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
