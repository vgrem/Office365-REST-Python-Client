from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.webs.web import Web
from tests import test_site_url, test_client_credentials

client = ClientContext(test_site_url).with_credentials(test_client_credentials)

result = client.web.get_all_webs().execute_query()
for web in result.value:  # type: Web
    print(web.url)
