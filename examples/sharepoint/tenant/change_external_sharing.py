"""
Set external sharing on site collections in Office 365

https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/set-external-sharing-on-site-collections-in-office-365
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sharing_capabilities import SharingCapabilities
from tests import test_admin_credentials, test_admin_site_url, test_team_site_url

admin_client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
site_props = admin_client.tenant.get_site_properties_by_url(test_team_site_url, True).execute_query()
default_value = SharingCapabilities.ExternalUserAndGuestSharing

if site_props.sharing_capability != default_value:
    print("Enabling external sharing on site: {0} ...".format(test_team_site_url))
    site_props.sharing_capability = default_value
    site_props.update().execute_query()
    print("Updated.")
else:
    print("External sharing has already been enabled on site: {0}".format(test_team_site_url))
