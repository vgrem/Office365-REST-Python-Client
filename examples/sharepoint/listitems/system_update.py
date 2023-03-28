import sys
from datetime import datetime, timedelta

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.user_value import FieldUserValue
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_team_site_url, test_client_credentials, test_user_principal_name

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

list_tasks = ctx.web.lists.get_by_title("Company Tasks")
items = list_tasks.items.get().top(1).execute_query()
if len(items) == 0:
    sys.exit("No items were found")

item_to_update = items[0]  # type: ListItem
author = ctx.web.site_users.get_by_email(test_user_principal_name)

modified_date = datetime.utcnow() - timedelta(days=3)
result = item_to_update.validate_update_list_item({
    "Title": "Task (updated)",
    "Author": FieldUserValue.from_user(author),
    "Modified": modified_date
}, dates_in_utc=True).execute_query()

has_any_error = any([item.HasException for item in result.value])
if has_any_error:
    print("Item update completed with errors, for details refer 'ErrorMessage' property")
else:
    print("Item has been updated successfully")
