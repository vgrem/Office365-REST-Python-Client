import sys
from datetime import date

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

list_tasks = ctx.web.lists.get_by_title("Requests")
items = list_tasks.items.get().top(1).execute_query()
if len(items) == 0:
    sys.exit("No items were found")

field_name = "DateColumn"
field_value = date.today()
items[0].set_property(field_name, field_value.isoformat()).update().execute_query()



