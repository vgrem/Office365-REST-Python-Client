"""
Demonstrates how to download large files.
"""

import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url


def print_download_progress(offset):
    # type: (int) -> None
    print("Downloaded '{0}' bytes...".format(offset))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "Shared Documents/archive/big_buck_bunny.mp4"
source_file = ctx.web.get_file_by_server_relative_path(file_url)
local_file_name = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
with open(local_file_name, "wb") as local_file:
    source_file.download_session(local_file, print_download_progress).execute_query()
print("[Ok] file has been downloaded: {0}".format(local_file_name))
