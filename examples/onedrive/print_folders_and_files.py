from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password


def enum_folders_and_files(root_folder):
    drive_items = root_folder.children.get().execute_query()
    for drive_item in drive_items:
        print("Name: {0}".format(drive_item.name))
        if not drive_item.is_property_available("folder"):  # is folder facet?
            enum_folders_and_files(drive_item)


client = GraphClient(acquire_token_by_username_password)
root = client.me.drive.root
enum_folders_and_files(root)
