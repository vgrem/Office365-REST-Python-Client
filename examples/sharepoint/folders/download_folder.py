import os
import tempfile

from settings import settings

from office365.runtime.auth.clientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(settings['url']).with_credentials(
    ClientCredential(settings['client_credentials']['client_id'],
                     settings['client_credentials']['client_secret']))

# retrieve files from library
source_folder = ctx.web.lists.get_by_title("Documents").rootFolder
files = source_folder.files
ctx.load(files)
ctx.execute_query()
download_path = tempfile.mkdtemp()
for file in files:
    print("Downloading file: {0} ...".format(file.properties["ServerRelativeUrl"]))
    download_file_name = os.path.join(download_path, os.path.basename(file.properties["Name"]))
    with open(download_file_name, "wb") as local_file:
        file.download(local_file)
        ctx.execute_query()
    print("[Ok] file has been downloaded: {0}".format(download_file_name))
