"""
Demonstrates how to delete multiple list items
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
items_count = 10

# 1. Load existing list items
tasks_list = ctx.web.lists.get_by_title("Company Tasks")
items = tasks_list.items.get().top(items_count).execute_query()

# 2. Delete list items (via batch mode)
[item.delete_object() for item in items]
ctx.execute_batch()
print("{0} items have been deleted".format(items_count))
