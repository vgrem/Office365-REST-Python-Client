import os
import tempfile

from office365.sharepoint.attachments.attachment import Attachment
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

download_path = tempfile.mkdtemp()

list_title = "Company Tasks"
source_list = ctx.web.lists.get_by_title(list_title)
items = source_list.items
ctx.load(items, ["ID", "UniqueId", "FileRef", "LinkFilename", "Title", "Attachments"])
ctx.execute_query()
for item in items:  # type: ListItem
    if item.properties['Attachments']:  # 1. determine whether ListItem contains attachments
        # 2. Explicitly load attachments for ListItem
        attachment_files = item.attachment_files.get().execute_query()
        # 3. Enumerate and save attachments
        for attachment_file in attachment_files:  # type: Attachment
            download_file_name = os.path.join(download_path, os.path.basename(attachment_file.file_name))
            with open(download_file_name, 'wb') as fh:
                attachment_file.download(fh).execute_query()
            print(f"{attachment_file.server_relative_url} has been downloaded into {download_file_name}")
