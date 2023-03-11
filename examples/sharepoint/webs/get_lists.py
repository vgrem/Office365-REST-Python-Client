from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.list import List
from tests import test_site_url, test_client_credentials

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
lists = client.web.get_lists().execute_query()
for lst in lists:  # type: List
    print(lst.title)
