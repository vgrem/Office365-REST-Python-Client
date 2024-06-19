"""
Demonstrates how to delete a List Item from a List
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
tasks_list = ctx.web.lists.get_by_title("Company Tasks")
items = tasks_list.items.get().execute_query()

print("Option 1: remove a list item (with an option to restore from a recycle bin)...")
items[0].recycle().execute_query()

print("Option 2: Permanently remove a list item...")
items[1].delete_object().execute_query()
