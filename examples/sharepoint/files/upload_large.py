import os

from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

target_url = "/sites/team/Shared Documents"
target_folder = ctx.web.get_folder_by_server_relative_url(target_url)
size_chunk = 1000000
local_path = "../../../tests/data/big_buck_bunny.mp4"
#local_path = "../../../tests/data/SharePoint User Guide.docx"


def print_upload_progress(offset):
    file_size = os.path.getsize(local_path)
    print("Uploaded '{0}' bytes from '{1}'...[{2}%]".format(offset, file_size, round(offset / file_size * 100, 2)))


with open(local_path, 'rb') as f:
    uploaded_file = target_folder.files.create_upload_session(f, size_chunk,
                                                              print_upload_progress).execute_query()

print('File {0} has been uploaded successfully'.format(uploaded_file.serverRelativeUrl))
