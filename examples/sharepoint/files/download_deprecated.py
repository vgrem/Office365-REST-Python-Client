"""
Demonstrates how to download a file from SharePoint site
Note: this method is considered a deprecated approach nowadays!
Refer download.py which demonstrates how to download a file
"""
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "Shared Documents/Sample.pdf"
download_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
with open(download_path, "wb") as local_file:
    file = ctx.web.get_file_by_server_relative_url(file_url).get().execute_query()
    resp = File.open_binary(ctx, file.properties["ServerRelativeUrl"])
    resp.raise_for_status()
    local_file.write(resp.content)
    print("[Ok] file has been downloaded into: {0}".format(download_path))
