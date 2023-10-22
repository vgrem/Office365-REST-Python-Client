"""
Example demonstrates how to download OneDrive files into local file system

https://learn.microsoft.com/en-us/onedrive/developer/rest-api/api/driveitem_get_content?view=odsp-graph-online
"""

import os
import tempfile

from office365.graph_client import GraphClient
from office365.onedrive.drives.drive import Drive
from tests import test_user_principal_name
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
drive = client.users[test_user_principal_name].drive  # type: Drive
with tempfile.TemporaryDirectory() as local_path:
    drive_items = drive.root.children.get().execute_query()
    file_items = [item for item in drive_items if item.file is not None]  # files only
    for drive_item in file_items:
        with open(os.path.join(local_path, drive_item.name), "wb") as local_file:
            drive_item.download(local_file).execute_query()  # download file content
        print("File '{0}' has been downloaded".format(local_file.name))
