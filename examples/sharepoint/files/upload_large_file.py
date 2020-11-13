import os

from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext


def print_upload_progress(offset, total_size):
    print("Uploaded '{}' bytes from '{}'...[{}%]".format(offset, total_size, round(offset/total_size*100, 2)))


credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])
ctx = ClientContext(settings['url']).with_credentials(credentials)

target_url = "/Shared Documents"
target_folder = ctx.web.get_folder_by_server_relative_url(target_url)
size_chunk = 1000000
local_path = "../../../tests/data/big_buck_bunny.mp4"

file_size = os.path.getsize(local_path)

if file_size > size_chunk:
    result_file = target_folder.files.create_upload_session(local_path, size_chunk, print_upload_progress)
else:
    with open(local_path, 'rb') as content_file:
        file_content = content_file.read()
    name = os.path.basename(local_path)
    result_file = target_folder.upload_file(name, file_content)
ctx.execute_query()
print('File {0} has been uploaded successfully'.format(result_file.serverRelativeUrl))
