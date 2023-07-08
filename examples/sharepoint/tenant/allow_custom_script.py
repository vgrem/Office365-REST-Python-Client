"""
Allow or prevent custom script

As a Global Administrator or SharePoint Administrator in Microsoft 365, you can allow custom script as a way
of letting users change the look, feel, and behavior of sites and pages to meet organizational objectives or
individual needs. If you allow custom script, all users who have "Add and Customize Pages" permission to a site
or page can add any script they want.
(By default, users who create sites are site owners and therefore have this permission.)

Demonstrates how to determine whether custom script on SharePoint site is enabled and enable  it if disabled

https://learn.microsoft.com/en-us/sharepoint/allow-or-prevent-custom-script
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.deny_add_and_customize_pages_status import \
    DenyAddAndCustomizePagesStatus
from tests import test_admin_site_url, test_admin_credentials, test_team_site_url

client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
site_props = client.tenant.get_site_properties_by_url(test_team_site_url, True).execute_query()
if site_props.deny_add_and_customize_pages == DenyAddAndCustomizePagesStatus.Disabled:
    print("Enabling custom script on site: {0}...".format(test_team_site_url))
    site_props.deny_add_and_customize_pages = DenyAddAndCustomizePagesStatus.Enabled
    site_props.update().execute_query()
    print("[Ok] Updated")
elif site_props.deny_add_and_customize_pages == DenyAddAndCustomizePagesStatus.Enabled:
    print("[Skipping] Custom script has already been allowed on site: {0}".format(test_team_site_url))
else:
    print("Unknown status detected")
