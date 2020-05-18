import os
import tempfile

from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.file import File
from settings import settings


def download_file_alt(context, file_url, local_path):
    """
    Download a file by server relative url
    :param local_path: str
    :param file_url: str
    :type context: ClientContext
    """
    response = File.open_binary(context, file_url)
    response.raise_for_status()
    with open(local_path, "wb") as local_file:
        local_file.write(response.content)


def download_file(remote_file, local_path):
    """
    Download a file by server relative url
    :param local_path: str
    :param remote_file: File
    """
    context = remote_file.context
    with open(local_path, "wb") as local_file:
        result = remote_file.download()
        context.execute_query()
        local_file.write(result.value)


ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))


# retrieve files from library
source_library = ctx.web.lists.get_by_title("Documents")
items_for_files = source_library.items.filter("FSObjType eq 0").select(["File"]).expand(["File"])
ctx.load(items_for_files)
ctx.execute_query()

# download files
download_path = tempfile.TemporaryDirectory()
for item in items_for_files:
    print("Downloading a file: {0}".format(item.file.properties['ServerRelativeUrl']))
    file_path = os.path.join(download_path.name, item.file.properties['Name'])
    download_file(item.file, file_path)
    print("[Ok] File: {0} has been downloaded.".format(file_path))
