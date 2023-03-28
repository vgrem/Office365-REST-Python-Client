from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

target_list = ctx.web.lists.get_by_title("Tasks")

list_tasks = ctx.web.lists.get_by_title("Tasks")
items = list_tasks.items.get().top(2).execute_query()

if len(items) < 2:
    print("No items found")

# Option 1: remove a list item (with an option to restore from a recycle bin)
item_id = items[0].id
target_list.get_item_by_id(item_id).recycle().execute_query()

# Option 2: Permanently remove a list item
item_id = items[1].id
target_item = target_list.get_item_by_id(item_id).delete_object().execute_query()




