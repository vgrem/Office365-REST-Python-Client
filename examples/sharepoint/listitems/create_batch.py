"""
Demonstrates how to create multiple list items
"""
from office365.sharepoint.client_context import ClientContext
from tests import create_unique_name, test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
tasks_list = ctx.web.lists.get_by_title("Company Tasks")

num_of_items = 10
item_props = {"Title": create_unique_name("Task")}
task_items = [tasks_list.add_item(item_props) for idx in range(0, num_of_items)]
ctx.execute_batch()
print("{0} task items created".format(len(task_items)))
