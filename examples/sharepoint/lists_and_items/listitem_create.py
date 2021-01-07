from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.field_multi_user_value import FieldMultiUserValue
from office365.sharepoint.fields.field_user_value import FieldUserValue
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType
from settings import settings
from tests import random_seed

credentials = ClientCredential(settings['client_credentials']['client_id'],
                               settings['client_credentials']['client_secret'])
ctx = ClientContext(settings.get('url')).with_credentials(credentials)

list_title = "Tasks N%s" % random_seed
list_create_info = ListCreationInformation(list_title,
                                           None,
                                           ListTemplateType.TasksWithTimelineAndHierarchy)

tasks_list = ctx.web.lists.add(list_create_info).execute_query()
current_user = ctx.web.current_user.get().execute_query()

multi_user_value = FieldMultiUserValue()
multi_user_value.add(FieldUserValue.from_user(current_user))

item_to_create = tasks_list.add_item({
    "Title": "New Task",
    "AssignedTo": multi_user_value
}).execute_query()


multi_user_value_alt = FieldMultiUserValue()
multi_user_value_alt.add(FieldUserValue(current_user.id))

item_to_create_alt = tasks_list.add_item({
    "Title": "New Task 2",
    "AssignedTo": multi_user_value_alt
}).execute_query()


print(f"List item added into list {list_title}")
