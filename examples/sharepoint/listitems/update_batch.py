from random import randint

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

# 1. Load existing list items
list_tasks = ctx.web.lists.get_by_title("Tasks")
items = list_tasks.items.get().top(10).execute_query()

# 2. Update list items via batch mode
for task_id, item in enumerate(items):
    task_prefix = str(randint(0, 10000))
    item.set_property("Title", "Task 123 {task_prefix}".format(task_prefix=task_prefix)).update()
ctx.execute_batch()
print("{0} items has been updated".format(len(items)))
