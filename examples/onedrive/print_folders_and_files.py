from office365.graph_client import GraphClient
from tests import acquire_token_by_username_password


def enum_folders_and_files(root_folder):
    drive_items = root_folder.children.get().execute_query()
    for drive_item in drive_items:
        item_type = drive_item.folder.is_server_object_null and "file" or "folder"
        print("Type: {0} Name: {1}".format(item_type, drive_item.name))
        if not drive_item.folder.is_server_object_null and drive_item.folder.childCount > 0:
            enum_folders_and_files(drive_item)


client = GraphClient(acquire_token_by_username_password)
root = client.me.drive.root
enum_folders_and_files(root)
