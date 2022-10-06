import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)


def download_files(source_folder, download_path):
    """
    Demonstrates how to enumerate folder files and download file's content

    :type source_folder: Folder
    :type download_path: str
    """

    # 1. retrieve file collection metadata from library root folder
    files = source_folder.files.get().execute_query()

    # 2. start download process (per file)
    for file in files:  # type: File
        print("Downloading file: {0} ...".format(file.properties["ServerRelativeUrl"]))
        download_file_name = os.path.join(download_path, os.path.basename(file.name))
        with open(download_file_name, "wb") as local_file:
            file.download(local_file).execute_query()
        print("[Ok] file has been downloaded: {0}".format(download_file_name))


def print_progress(download_path):
    """
    :type download_path: str
    """
    print("({0} of {1}) [Ok] file has been downloaded: {2}".format(0, 0, download_path))


to_path = tempfile.mkdtemp()
from_folder = ctx.web.lists.get_by_title("Documents").root_folder
# from_folder.download(to_path, print_progress).execute_query()
download_files(from_folder, to_path)
