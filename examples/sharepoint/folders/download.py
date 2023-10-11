"""
Demonstrates how to enumerate folder files and download file's content
"""
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url


def print_progress(file):
    # type: (File) -> None
    print("File {0} has been  downloaded".format(file.serverRelativeUrl))


def download_files(source_folder, download_path):
    # type: (Folder, str) -> None

    # 1. retrieve files collection (metadata) from library root folder
    files = source_folder.files.get().execute_query()

    # 2. start download process (per file)
    for file in files:
        print("Downloading file: {0} ...".format(file.properties["ServerRelativeUrl"]))
        download_file_name = os.path.join(download_path, file.name)
        with open(download_file_name, "wb") as local_file:
            file.download(local_file).execute_query()
        print("[Ok] file has been downloaded: {0}".format(download_file_name))


to_path = tempfile.mkdtemp()
ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
from_folder = ctx.web.lists.get_by_title("Documents").root_folder
download_files(from_folder, to_path)
