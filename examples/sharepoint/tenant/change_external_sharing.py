from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sharing_capabilities import SharingCapabilities
from tests import test_user_credentials

target_site_url = "https://mediadev8.sharepoint.com/sites/team"

admin_client = ClientContext(target_site_url).with_credentials(test_user_credentials)
site_props = admin_client.tenant.get_site_properties_by_url(target_site_url, True).execute_query()
if site_props.properties.get("SharingCapability") != SharingCapabilities.ExternalUserSharingOnly:
    print("Changing external sharing on site: {0}...".format(target_site_url))
    site_props.set_property('SharingCapability', SharingCapabilities.ExternalUserSharingOnly).update().execute_query()
    print("Updated.")
