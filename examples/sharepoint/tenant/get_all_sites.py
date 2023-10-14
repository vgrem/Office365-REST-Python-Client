"""
Retrieves sites in tenant
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url

admin_client = ClientContext(test_admin_site_url).with_credentials(
    test_admin_credentials
)
result = admin_client.tenant.get_site_properties_from_sharepoint_by_filters(
    ""
).execute_query()
i = 0
for siteProps in result:
    print("({0} of {1}) {2}".format(i, len(result), siteProps.url))
    i += 1
