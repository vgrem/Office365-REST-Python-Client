"""
Creates a list item in a List
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.user_value import FieldUserValue
from tests import test_client_credentials, test_team_site_url, test_user_principal_name

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
tasks_list = ctx.web.lists.get_by_title("Company Tasks")
manager = ctx.web.site_users.get_by_principal_name(test_user_principal_name)

item = tasks_list.add_item(
    {
        "Title": "New Task",
        # "Manager": FieldUserValue.from_user(manager),
    }
).execute_query()
print("Item has been created")
