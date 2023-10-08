"""
Retrieves site collection administrators
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_site_url

client = ClientContext(test_site_url).with_credentials(test_admin_credentials)
result = client.site.get_site_administrators().execute_query()
for info in result.value:
    print(info)
