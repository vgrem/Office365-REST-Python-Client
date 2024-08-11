"""
Demonstrates how to create multiple list items
"""

from typing import List

from office365.runtime.client_object import ClientObject
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import create_unique_name, test_client_credentials, test_team_site_url


def print_progress(return_types):
    # type: (List[ClientObject]) -> None
    items_count = len([t for t in return_types if isinstance(t, ListItem)])
    print("{0} list items has been created".format(items_count))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
tasks_list = ctx.web.lists.get_by_title("Company Tasks")

num_of_items = 512
item_props = {"Title": create_unique_name("Task")}
task_items = [tasks_list.add_item(item_props) for idx in range(0, num_of_items)]
ctx.execute_batch(success_callback=print_progress)
print("{0} task items created".format(len(task_items)))
