import os
import tempfile

from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml import CamlQuery

download_path = tempfile.mkdtemp()

client_creds = ClientCredential(settings['client_credentials']['client_id'],
                                settings['client_credentials']['client_secret'])
ctx = ClientContext(settings['url']).with_credentials(client_creds)

list_obj = ctx.web.lists.get_by_title("Tasks123")
items = list_obj.get_items(CamlQuery.create_all_items_query())
ctx.execute_query()
for item in items:
    if item.properties['Attachments']:  # 1. determine whether ListItem contains attachments
        # 2. Explicitly load attachments for ListItem
        attachment_files = item.attachmentFiles
        ctx.load(attachment_files)
        ctx.execute_query()
        # 3. Enumerate and save attachments
        for attachment_file in attachment_files:
            download_file_name = os.path.join(download_path, os.path.basename(attachment_file.properties["FileName"]))
            with open(download_file_name, 'wb') as fh:
                content = attachment_file.read()
                fh.write(content)
