import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_user_credentials, test_site_url

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
lib_title = "Documents"
lib = ctx.web.lists.get_by_title(lib_title)
recent_items = lib.items.order_by("Created desc").select(["ID", "FileRef"]).top(1).get().execute_query()
for item in recent_items:  # type: ListItem
    file_url = item.properties.get("FileRef")
    download_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
    with open(download_path, "wb") as local_file:
        item.file.download(local_file).execute_query()
    print("[Ok] file has been downloaded into: {0}".format(download_path))
