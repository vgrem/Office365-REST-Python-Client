"""
Demonstrates how to download folders content into a zip file
"""

import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests import test_client_credentials, test_team_site_url


def print_progress(file):
    # type: (File) -> None
    print("File {0} has been  downloaded".format(file.serverRelativeUrl))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
from_folder = ctx.web.lists.get_by_title("Documents").root_folder
zip_path = os.path.join(tempfile.mkdtemp(), "download.zip")
with open(zip_path, "wb") as to_file:
    from_folder.download_folder(to_file, print_progress).execute_query()
    print("Files has been downloaded: {0}".format(zip_path))
