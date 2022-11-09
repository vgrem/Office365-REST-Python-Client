from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials

client = ClientContext(test_site_url).with_credentials(test_client_credentials)

web = client.web.get().expand(["Author"]).execute_query()
print(web.author.user_principal_name)
