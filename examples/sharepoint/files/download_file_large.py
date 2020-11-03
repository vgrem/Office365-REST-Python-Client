import os
import tempfile

from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext


def download_file(context, download_url, file_object, chunk_downloaded=None, chunk_size=1024 * 1024):
    """

    :type context: office365.sharepoint.client_context.ClientContext
    :type download_url: str
    :type file_object: typing.IO
    :type chunk_downloaded: (int)->None or None
    :type chunk_size: int
    """

    request = RequestOptions(
        r"{0}web/getFileByServerRelativeUrl('{1}')/\$value".format(ctx.service_root_url(), download_url))
    request.stream = True
    response = context.execute_request_direct(request)
    response.raise_for_status()
    bytes_read = 0
    for chunk in response.iter_content(chunk_size=chunk_size):
        bytes_read += len(chunk)
        if callable(chunk_downloaded):
            chunk_downloaded(bytes_read)
        file_object.write(chunk)


def print_download_progress(offset):
    print("Downloaded '{0}' bytes...".format(offset))


site_url = settings.get('url') + "/sites/team"
credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                               settings.get('client_credentials').get('client_secret'))
ctx = ClientContext(site_url).with_credentials(credentials)

file_url = '/sites/team/Shared Documents/big_buck_bunny.mp4'
local_file_name = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
with open(local_file_name, "wb") as local_file:
    download_file(ctx, file_url, local_file, print_download_progress)
print("[Ok] file has been downloaded: {0}".format(local_file_name))
