from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
items_count = 2

# 1. Load existing list items
list_tasks = ctx.web.lists.get_by_title("Tasks")
items = list_tasks.items.get().top(items_count).execute_query()

# 2. Delete list items (via batch mode)
for item in items:  # type: ListItem
    item.delete_object()
ctx.execute_batch()
print("{0} items have been deleted".format(items_count))
