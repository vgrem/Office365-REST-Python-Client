"""
When using SharePoint Online you can define applications in Azure AD and these applications can
be granted permissions to SharePoint, but also to all the other services in Office 365.
This model is the preferred model in case you're using SharePoint Online, if you're using SharePoint on-premises
you have to use the SharePoint Only model via based Azure ACS as described in here:

Demonstrates how to use Azure AD App-Only auth flow

https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread
"""

import os

from examples import sample_client_id, sample_tenant_name, sample_thumbprint, sample_site_url
from office365.sharepoint.client_context import ClientContext

cert_credentials = {
    'tenant': sample_tenant_name,
    'client_id': sample_client_id,
    'thumbprint': sample_thumbprint,
    'cert_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__)),
}
ctx = ClientContext(sample_site_url).with_client_certificate(**cert_credentials)
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
