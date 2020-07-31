from settings import settings

from office365.graph.graph_client import GraphClient


def get_token_for_user(auth_ctx):
    """
    Acquire token via user credentials

    :type auth_ctx: adal.AuthenticationContext
    """
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


def enum_folders_and_files(root_folder):
    drive_items = root_folder.children
    client.load(drive_items)
    client.execute_query()
    for drive_item in drive_items:
        item_type = drive_item.folder.is_server_object_null and "file" or "folder"
        print("Type: {0} Name: {1}".format(item_type, drive_item.name))
        if not drive_item.folder.is_server_object_null and drive_item.folder.childCount > 0:
            enum_folders_and_files(drive_item)


client = GraphClient(settings['tenant'], get_token_for_user)
root = client.me.drive.root
enum_folders_and_files(root)
