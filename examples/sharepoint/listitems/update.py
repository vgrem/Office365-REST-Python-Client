import sys
from random import randint

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.field_value import TaxonomyFieldValue
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

list_tasks = ctx.web.lists.get_by_title("Tasks")
items = list_tasks.items.get().top(1).execute_query()
if len(items) == 0:
    sys.exit("No items found")

item_to_update = items[0]
task_prefix = str(randint(0, 10000))
# tax_field_value = TaxonomyFieldValue("Sweden", "f9a6dae9-633c-474b-b35e-b235cf2b9e73")
# item_to_update.set_property("Country", tax_field_value).update().execute_query()
item_to_update.set_property("Title", f"Task {task_prefix}").update().execute_query()
print("Item has been updated")


