from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings

ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

# 1. Load list items
list_tasks = ctx.web.lists.get_by_title("Tasks")
items = list_tasks.items
ctx.load(items)
ctx.execute_query()
# 2. Update list items
for task_id, item in enumerate(items):
    item.set_property("Title", f"Task d000{task_id}")
    item.update()
ctx.execute_batch()
