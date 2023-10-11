from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

client = ClientContext(test_site_url).with_credentials(test_client_credentials)

webs = client.web.get_all_webs().execute_query()
for web in webs:  # type: Web
    print(web.url)
