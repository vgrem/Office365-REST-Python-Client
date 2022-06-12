from office365.sharepoint.attachments.attachment import Attachment
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_title = "Company Tasks"
source_list = ctx.web.lists.get_by_title(list_title)
items = source_list.items.select(["Id"]).expand(["AttachmentFiles"]).get().execute_query()
for item in items:  # type: ListItem
    for attachment_file in item.attachment_files:  # type: Attachment
        print(f"{attachment_file.server_relative_url}")
