import os
import tempfile

from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext


def print_download_progress(offset):
    print("Downloaded '{0}' bytes...".format(offset))


site_url = settings.get('url') + "/sites/team"
credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                               settings.get('client_credentials').get('client_secret'))
ctx = ClientContext(site_url).with_credentials(credentials)

file_url = '/sites/team/Shared Documents/big_buck_bunny.mp4'
source_file = ctx.web.get_file_by_server_relative_url(file_url)
local_file_name = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
with open(local_file_name, "wb") as local_file:
    source_file.download_session(local_file, print_download_progress).execute_query()
print("[Ok] file has been downloaded: {0}".format(local_file_name))
