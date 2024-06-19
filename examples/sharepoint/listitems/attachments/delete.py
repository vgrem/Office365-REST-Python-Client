"""
Deletes attachments from a List
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_title = "Company Tasks"
tasks_list = ctx.web.lists.get_by_title(list_title)
task_items = tasks_list.items.get().execute_query()
for task_item in task_items:
    task_item.attachment_files.delete_all().execute_query()
    print("Attachments have been deleted for list item {0}".format(task_item.id))
