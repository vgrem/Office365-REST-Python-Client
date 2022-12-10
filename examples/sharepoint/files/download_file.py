import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
# file_url = '/sites/team/Shared Documents/big_buck_bunny.mp4'
file_url = "/sites/team/Shared Documents/!2022/Financial Sample.xlsx"
download_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
with open(download_path, "wb") as local_file:
    file = ctx.web.get_file_by_server_relative_url(file_url).download(local_file).execute_query()
    #file = ctx.web.get_file_by_server_relative_url(file_url).download(local_file).execute_query()
print("[Ok] file has been downloaded into: {0}".format(download_path))
