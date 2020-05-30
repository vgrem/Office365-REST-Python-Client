import os
import tempfile

from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings

ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

# retrieve files from library
source_folder = ctx.web.lists.get_by_title("Documents").rootFolder
files = source_folder.files
# items_for_files = source_library.items.filter("FSObjType eq 0").select(["File"]).expand(["File"])
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
