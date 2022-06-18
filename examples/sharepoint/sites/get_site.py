from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
site = client.site.get().execute_query()
print("Site url: {}".format(site.url))

result = site.is_valid_home_site().execute_query()
print("Landing Intranet site: {}".format(result.value))
