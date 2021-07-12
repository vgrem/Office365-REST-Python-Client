from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)

# get target folder by path (where 'archive' is a folder path)
folder_item = client.me.drive.root.get_by_path("archive")
local_path = "../../tests/data/big_buck_bunny.mp4"


def print_progress(range_pos):
    print("{0} bytes uploaded".format(range_pos))


# upload a file
file_item = folder_item.resumable_upload(local_path, chunk_uploaded=print_progress).execute_query()
print(f"File {file_item.web_url} has been uploaded")
