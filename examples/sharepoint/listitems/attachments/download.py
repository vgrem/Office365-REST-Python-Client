"""
Demonstrates how to download list item attachments
"""

import os
import tempfile

from office365.sharepoint.attachments.attachment import Attachment
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url


def print_progress(attachment_file):
    # type: (Attachment) -> None
    print("{0} has been downloaded".format(attachment_file.server_relative_url))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

list_title = "Company Tasks"
source_list = ctx.web.lists.get_by_title(list_title)
items = source_list.items.get().execute_query()
for item in items:
    zip_path = os.path.join(tempfile.mkdtemp(), "attachments_{0}.zip".format(item.id))
    with open(zip_path, "wb") as f:
        item.attachment_files.download(f, print_progress).execute_query()
    print("{0} attachments has been downloaded...".format(zip_path))
