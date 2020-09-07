from random import randint

from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

# 1. Load existing list items
list_tasks = ctx.web.lists.get_by_title("Tasks")
items = list_tasks.items.get().execute_query()
# 2. Update list items via Batch mode
for task_id, item in enumerate(items):
    task_prefix = str(randint(0, 10000))
    item.set_property("Title", f"Task {task_prefix}")
    item.update()
ctx.execute_batch()
