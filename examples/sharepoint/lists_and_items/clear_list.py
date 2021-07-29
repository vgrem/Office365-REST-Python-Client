from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

target_list = ctx.web.lists.get_by_title("Tasks")
items = target_list.items.get().execute_query()
for item in items:  # type: ListItem
    item.delete_object()
ctx.execute_batch()
print("Items deleted count: {0}".format(len(items)))
