"""
Demonstrates how to create multiple list items via batch request
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.template_type import ListTemplateType
from tests import create_unique_name, test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_tasks = ctx.web.add_list(
    create_unique_name("Tasks"), ListTemplateType.Tasks
).execute_query()

num_of_items = 2
item_props = {"Title": create_unique_name("Task")}
task_items = [list_tasks.add_item(item_props) for idx in range(0, num_of_items)]
ctx.execute_batch()
print("{0} task items created".format(len(task_items)))


print("Cleaning up temporary resources...")
list_tasks.delete_object().execute_query()
