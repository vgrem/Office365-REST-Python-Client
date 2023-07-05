"""
Download the contents of a DriveItem (file)

https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0&tabs=http
"""
import os
import tempfile

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
# 1. address file by path
# remote_path = "archive/countries.json"
remote_path = "archive/Sample.rtf"
remote_file = client.me.drive.root.get_by_path(remote_path)
# 2. download file content
with tempfile.TemporaryDirectory() as local_path:
    with open(os.path.join(local_path, os.path.basename(remote_path)), 'wb') as local_file:
        remote_file.download(local_file).execute_query()
    print("File has been downloaded into {0}".format(local_file.name))
