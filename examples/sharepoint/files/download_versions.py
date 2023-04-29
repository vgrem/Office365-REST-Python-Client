import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.versions.version import FileVersion
from tests import test_team_site_url, test_client_credentials


def download_file_versions(source_file, target_path):
    """
    :type source_file: office365.sharepoint.files.file.File
    :type target_path: str
    """
    file_versions = source_file.versions.get().execute_query()
    for version in file_versions:  # type: FileVersion
        with open(target_path, "wb") as f:
            file = version.download(f).execute_query()
        print("[Ok] file version {0} has been downloaded into: {1}".format(version.url, target_path))


def download_specific_file_version(source_file, version, target_path):
    """
    :type source_file: office365.sharepoint.files.file.File
    :type version: int
    :type target_path: str
    """
    version = source_file.versions.get_by_id(version)
    with open(target_path, "wb") as f:
        file = version.download(f).execute_query()
    print("[Ok] file version {0} has been downloaded into: {1}".format(version.url, target_path))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "/sites/team/Shared Documents/report #123.csv"
remote_file = ctx.web.get_file_by_server_relative_path(file_url)
local_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
#download_file_versions(remote_file, local_path)
download_specific_file_version(remote_file, 1, local_path)
