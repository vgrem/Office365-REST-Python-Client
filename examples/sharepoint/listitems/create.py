from examples.sharepoint import create_sample_tasks_list
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.multi_user_value import FieldMultiUserValue
from office365.sharepoint.fields.user_value import FieldUserValue
from tests import test_site_url, test_client_credentials, test_user_principal_name


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
tasks_list = create_sample_tasks_list(ctx.web)

user = ctx.web.ensure_user(test_user_principal_name)
multi_user_value = FieldMultiUserValue()
multi_user_value.add(FieldUserValue.from_user(user))

item_to_create = tasks_list.add_item({
    "Title": "New Task",
    "AssignedTo": multi_user_value,
    "Manager": FieldUserValue.from_user(user)
}).execute_query()

multi_user_value_alt = FieldMultiUserValue()
multi_user_value_alt.add(FieldUserValue(user.id))

item_to_create_alt = tasks_list.add_item({
    "Title": "New Task 2",
    "AssignedTo": multi_user_value_alt
}).execute_query()
