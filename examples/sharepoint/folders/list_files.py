"""
Gets the files from the folder.
If 'recursive' flag set to True, it traverses all sub folders
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests import test_team_site_url, test_user_credentials


def print_file(f):
    # type: (File) -> None
    print(f.serverRelativeUrl)


ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
target_folder_url = "Shared Documents"
root_folder = ctx.web.get_folder_by_server_relative_path(target_folder_url)
files = root_folder.get_files(True).execute_query()
[print_file(f) for f in files]
