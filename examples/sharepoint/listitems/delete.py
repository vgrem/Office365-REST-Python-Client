"""
Demonstrates how to delete a list item
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.template_type import ListTemplateType
from tests import create_unique_name, test_client_credentials, test_team_site_url


def create_tasks_list(client):
    """
    :type client: ClientContext
    """
    list_title = create_unique_name("Tasks")
    target_list = client.web.add_list(list_title, ListTemplateType.Tasks)
    target_list.add_item({"Title": "Task1"})
    target_list.add_item({"Title": "Task2"})
    return target_list.expand(["items"]).get()


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
tasks_list = create_tasks_list(ctx).execute_query()

print("Option 1: remove a list item (with an option to restore from a recycle bin)...")
item_id = tasks_list.items[1].id
tasks_list.get_item_by_id(item_id).recycle().execute_query()

print("Option 2: Permanently remove a list item...")
item_id = tasks_list.items[2].id
tasks_list.get_item_by_id(item_id).delete_object().execute_query()


print("Cleaning up...")
tasks_list.delete_object().execute_query()
