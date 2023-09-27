"""
Demonstrates how to download folders content into a zip file
"""
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil
from tests import test_team_site_url, test_client_credentials


def print_progress(file):
    print("File {0} has been  downloaded".format(file.serverRelativeUrl))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
from_folder = ctx.web.lists.get_by_title("Documents").root_folder
zip_path = os.path.join(tempfile.mkdtemp(), "download.zip")
with open(zip_path, "wb") as local_file:
    MoveCopyUtil.download_folder_as_zip(from_folder, local_file, print_progress).execute_query()
    print("Files has been downloaded: {0}".format(zip_path))
