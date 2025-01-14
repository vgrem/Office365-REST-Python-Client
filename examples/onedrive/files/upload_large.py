"""
Demonstrates how to upload a large file

https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username


def print_progress(range_pos):
    # type: (int) -> None
    print("{0} bytes uploaded".format(range_pos))


client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
chunk_size = 1 * 1024 * 1024
local_path = "../../../tests/data/big_buck_bunny.mp4"
remote_folder = client.me.drive.root.get_by_path("archive")
remote_file = (
    remote_folder.resumable_upload(
        local_path, chunk_size=chunk_size, chunk_uploaded=print_progress
    )
    .get()
    .execute_query()
)
print("File {0} has been uploaded".format(remote_file.web_url))
