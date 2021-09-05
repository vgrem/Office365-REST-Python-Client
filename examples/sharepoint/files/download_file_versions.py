import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file_version import FileVersion
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "/sites/team/Shared Documents/report #123.csv"
file_versions = ctx.web.get_file_by_server_relative_path(file_url).versions.get().execute_query()
for version in file_versions:  # type: FileVersion
    download_path = os.path.join(tempfile.mkdtemp(), version.version_label + "_" + os.path.basename(file_url))
    with open(download_path, "wb") as local_file:
        file = version.download(local_file).execute_query()
    print("[Ok] file version {0} has been downloaded into: {1}".format(version.url, download_path))


version = ctx.web.get_file_by_server_relative_path(file_url).versions.get_by_id(512)
download_path = os.path.join(tempfile.mkdtemp(),  os.path.basename(file_url))
with open(download_path, "wb") as local_file:
    file = version.download(local_file).execute_query()
print("[Ok] file version {0} has been downloaded into: {1}".format(version.url, download_path))

