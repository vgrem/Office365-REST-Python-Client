import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials

ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)

# 1. retrieve file collection metadata from library root folder
files = ctx.web.lists.get_by_title("Documents").root_folder.files.get().execute_query()
# 2. start download process (per file)
download_path = tempfile.mkdtemp()
for file in files:
    print("Downloading file: {0} ...".format(file.properties["ServerRelativeUrl"]))
    download_file_name = os.path.join(download_path, os.path.basename(file.properties["Name"]))
    with open(download_file_name, "wb") as local_file:
        file.download(local_file)
        ctx.execute_query()
    print("[Ok] file has been downloaded: {0}".format(download_file_name))
