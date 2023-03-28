from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.multi_user_value import FieldMultiUserValue
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.fields.user_value import FieldUserValue
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType
from tests import create_unique_name, test_site_url, test_client_credentials, test_user_principal_name


def create_tasks_list(client):
    """

    :type client: ClientContext
    """
    list_title = create_unique_name("Tasks N")
    list_create_info = ListCreationInformation(list_title,
                                               None,
                                               ListTemplateType.TasksWithTimelineAndHierarchy)

    target_list = client.web.lists.add(list_create_info).execute_query()
    field_info = FieldCreationInformation("Manager", FieldType.User)
    user_field = target_list.fields.add(field_info).execute_query()
    return target_list


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
tasks_list = create_tasks_list(ctx)

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

