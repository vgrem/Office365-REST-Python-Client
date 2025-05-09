""" """

from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url, test_team_site_url

client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
site_props = client.tenant.get_site_properties_by_url(
    test_team_site_url, True
).execute_query()
print(site_props)
