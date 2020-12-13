import os
from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])
ctx = ClientContext(settings['url']).with_credentials(credentials)

target_url = "/Shared Documents"
target_folder = ctx.web.get_folder_by_server_relative_url(target_url)
size_chunk = 1000000
local_path = "../../../tests/data/big_buck_bunny.mp4"
# local_path = "../../../tests/data/SharePoint User Guide.docx"

file_size = os.path.getsize(local_path)


def print_upload_progress(offset):
    print("Uploaded '{}' bytes from '{}'...[{}%]".format(offset, file_size, round(offset / file_size * 100, 2)))


uploaded_file = target_folder.files.create_upload_session(local_path, size_chunk, print_upload_progress)
ctx.execute_query()
print('File {0} has been uploaded successfully'.format(uploaded_file.serverRelativeUrl))
