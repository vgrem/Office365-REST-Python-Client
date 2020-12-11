import os
import tempfile

from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

creds = ClientCredential(settings.get('client_credentials').get('client_id'),
                         settings.get('client_credentials').get('client_secret'))
ctx = ClientContext(settings['url']).with_credentials(creds)

download_path = tempfile.mkdtemp()

list_title = "Tasks"
source_list = ctx.web.lists.get_by_title(list_title)
# items = list_obj.get_items(CamlQuery.create_all_items_query())
# items = list_obj.get_items()
items = source_list.items
ctx.load(items, ["ID", "UniqueId", "FileRef", "LinkFilename", "Title", "Attachments"])
ctx.execute_query()
for item in items:
    if item.properties['Attachments']:  # 1. determine whether ListItem contains attachments
        # 2. Explicitly load attachments for ListItem
        attachment_files = item.attachment_files
        ctx.load(attachment_files)
        ctx.execute_query()
        # 3. Enumerate and save attachments
        for attachment_file in attachment_files:
            download_file_name = os.path.join(download_path, os.path.basename(attachment_file.properties["FileName"]))
            with open(download_file_name, 'wb') as fh:
                content = attachment_file.read()
                fh.write(content)
                print(f"{attachment_file.server_relative_url} has been downloaded")
