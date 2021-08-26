from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url, create_unique_name

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_tasks = ctx.web.lists.get_by_title("Tasks")

task_items = [list_tasks.add_item({"Title": create_unique_name("Task")}) for idx in range(0, 9)]
ctx.execute_batch()
print(" {0} task items created".format(len(task_items)))
