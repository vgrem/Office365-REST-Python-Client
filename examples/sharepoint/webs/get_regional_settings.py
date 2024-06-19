"""
Retrieves the locale settings of a site
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
result = client.web.regional_settings.get().execute_query()
print(result)
