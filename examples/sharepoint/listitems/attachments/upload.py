"""
Creates a list item and uploads an attachment
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_title = "Company Tasks"
tasks_list = ctx.web.lists.get_by_title(list_title)

# 1. create a new list item
task_item = tasks_list.add_item({"Title": "New Task"}).execute_query()

# task_item.attachment_files.delete_all().execute_query()

# 2. read & upload attachment for a list item
path = "../../../data/Financial Sample.xlsx"
with open(path, "rb") as f:
    attachment = task_item.attachment_files.upload(f).execute_query()
print(attachment)
