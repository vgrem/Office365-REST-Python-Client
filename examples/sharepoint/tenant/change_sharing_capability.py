"""
Set external sharing on site collections in Office 365

https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/set-external-sharing-on-site-collections-in-office-365
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sharing_capabilities import (
    SharingCapabilities,
)
from tests import (
    test_admin_site_url,
    test_cert_thumbprint,
    test_client_id,
    test_team_site_url,
    test_tenant,
)

admin_client = ClientContext(test_admin_site_url).with_client_certificate(
    test_tenant, test_client_id, test_cert_thumbprint, "../../selfsignkey.pem"
)

# admin_client = ClientContext(test_admin_site_url).with_credentials(
#    test_admin_credentials
# )

site_props = admin_client.tenant.get_site_properties_by_url(
    test_team_site_url
).execute_query()
site_props.sharing_capability = SharingCapabilities.ExternalUserAndGuestSharing
site_props.update().execute_query()
