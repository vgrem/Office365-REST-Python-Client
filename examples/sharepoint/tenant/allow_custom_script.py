from office365.sharepoint.client_context import ClientContext
from tests import test_admin_site_url, test_admin_credentials, test_team_site_url

client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
site_props = client.tenant.get_site_properties_by_url(test_team_site_url, True).execute_query()
if site_props.deny_add_and_customize_pages:
    print("Enabling custom script on site: {0}...".format(test_team_site_url))
    site_props.deny_add_and_customize_pages = False
    site_props.update().execute_query()
    print("Done.")
else:
    print("Custom script has already been allowed on site: {0}".format(test_team_site_url))
