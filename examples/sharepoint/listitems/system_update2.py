import sys

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)

target_list = ctx.web.lists.get_by_title("Documents")
items = target_list.items.get().top(1).execute_query()
if len(items) == 0:
    sys.exit("No items were found")

item = items[0]
item.system_update().execute_query()
