from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from tests.graph_case import acquire_token_by_username_password


def enum_folders_and_files(root_folder):
    # type: (DriveItem) ->  None
    drive_items = root_folder.children.get().execute_query()
    for drive_item in drive_items:
        print("Name: {0}".format(drive_item.web_url))
        if drive_item.is_folder:  # is folder facet?
            enum_folders_and_files(drive_item)


client = GraphClient(acquire_token_by_username_password)
root = client.me.drive.root
enum_folders_and_files(root)
