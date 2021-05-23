from random import randint

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

list_tasks = ctx.web.lists.get_by_title("Tasks")
items = list_tasks.items.get().top(1).execute_query()  # 1. Load existing list items
if len(items) > 0:
    item_to_update = items[0]
    task_prefix = str(randint(0, 10000))
    item_to_update.set_property("Title", f"Task {task_prefix}")
    item_to_update.update().execute_query()


