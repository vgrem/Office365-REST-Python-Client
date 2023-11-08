"""
Gets site basic properties
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
site = client.site.get().execute_query()
print("Site url: {}".format(site.url))

result = site.is_valid_home_site().execute_query()
print("Is home site: {}".format(result.value))
