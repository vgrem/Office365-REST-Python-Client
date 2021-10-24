import os

from office365.sharepoint.attachments.attachmentfile_creation_information import AttachmentfileCreationInformation
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

list_title = "Tasks"
tasks_list = ctx.web.lists.get_by_title(list_title)

# 1. create a new list item
task_item = tasks_list.add_item({
    "Title": "New Task"
}).execute_query()

# 2. read & upload attachment for a list item
path = "../../data/report #123.csv"
with open(path, 'rb') as fh:
    file_content = fh.read()
attachment_file_info = AttachmentfileCreationInformation(os.path.basename(path), file_content)
task_item.attachment_files.add(attachment_file_info).execute_query()
