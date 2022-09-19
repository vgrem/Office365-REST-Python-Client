from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials

target_site_url = "https://mediadev8.sharepoint.com/sites/team"

client = ClientContext(target_site_url).with_credentials(test_user_credentials)
site_props = client.tenant.get_site_properties_by_url(target_site_url, True).execute_query()
if site_props.deny_add_and_customize_pages:
    print("Enabling custom script on site: {0}...".format(target_site_url))
    site_props.deny_add_and_customize_pages = False
    site_props.update().execute_query()
    print("Updated.")
