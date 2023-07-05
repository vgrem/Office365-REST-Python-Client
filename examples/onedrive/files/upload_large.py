"""
Demonstrates how to upload a large file

https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)

chunk_size = 3 * 1024 * 1024


def print_progress(range_pos):
    print("{0} bytes uploaded".format(range_pos))


local_path = "../../../tests/data/big_buck_bunny.mp4"
remote_folder = client.me.drive.root.get_by_path("archive")
remote_file = remote_folder.resumable_upload(local_path, chunk_size=chunk_size,
                                             chunk_uploaded=print_progress).get().execute_query()
print(f"File {remote_file.web_url} has been uploaded")
