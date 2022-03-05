from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)


def enum_folder(parent_folder, fn):
    """
    :type parent_folder: Folder
    :type fn: (File)-> None
    """
    parent_folder.expand(["Files", "Folders"]).get().execute_query()
    for file in parent_folder.files:  # type: File
        fn(file)
    for folder in parent_folder.folders:  # type: Folder
        enum_folder(folder, fn)


def print_file(f):
    print(f.properties['ServerRelativeUrl'])


target_folder_url = "Shared Documents/Archive"
root_folder = ctx.web.get_folder_by_server_relative_url(target_folder_url)
enum_folder(root_folder, print_file)
