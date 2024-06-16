"""
Demonstrates how to download list item attachments
"""
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

download_path = tempfile.mkdtemp()
list_title = "Company Tasks"

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
source_list = ctx.web.lists.get_by_title(list_title)
items = source_list.items.get().execute_query()
for item in items:
    attachment_files = item.attachment_files.get().execute_query()
    for attachment_file in attachment_files:
        download_file_name = os.path.join(
            download_path, os.path.basename(attachment_file.file_name)
        )
        with open(download_file_name, "wb") as fh:
            attachment_file.download(fh).execute_query()
        print(
            f"{attachment_file.server_relative_url} has been downloaded into {download_file_name}"
        )

