from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sharing_capabilities import SharingCapabilities
from tests import test_admin_credentials, test_admin_site_url, test_team_site_url

admin_client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
site_props = admin_client.tenant.get_site_properties_by_url(test_team_site_url, True).execute_query()
if site_props.properties.get("SharingCapability") != SharingCapabilities.ExternalUserSharingOnly:
    print("Enabling external sharing on site: {0}...".format(test_team_site_url))
    site_props.set_property('SharingCapability', SharingCapabilities.ExternalUserSharingOnly).update().execute_query()
    print("Updated.")
else:
    print("External sharing has already been enabled on site: {0}".format(test_team_site_url))
