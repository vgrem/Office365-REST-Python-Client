import os
import tempfile

from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings

ctx = ClientContext.connect_with_credentials(settings.get('url') + "/sites/team",
                                             ClientCredential(settings.get('client_credentials').get('client_id'),
                                                              settings.get('client_credentials').get('client_secret')))

# file_url = "/sites/team/Shared Documents/sample.docx"
file_url = '/sites/team/Shared Documents/big_buck_bunny.mp4'
download_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
with open(download_path, "wb") as local_file:
    source_file = ctx.web.get_file_by_server_relative_url(file_url)
    source_file.download(local_file)
    ctx.execute_query()
    print("[Ok] file has been downloaded: {0}".format(download_path))
