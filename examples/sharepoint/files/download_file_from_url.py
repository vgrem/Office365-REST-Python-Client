import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.UserCredential import UserCredential

ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File
print(dir(UserCredential))
# from settings import settings
#
# abs_file_url = "{site_url}sites/team/Shared Documents/sample.docx".format(site_url=settings.get('url'))
# user_credentials = UserCredential(settings.get('user_credentials').get('username'),
#                                   settings.get('user_credentials').get('password'))
#
#
# file_name = os.path.basename(abs_file_url)
# with tempfile.TemporaryDirectory() as local_path:
#     with open(os.path.join(local_path, file_name), 'wb') as local_file:
#         file = File.from_url(abs_file_url).with_credentials(user_credentials).download(local_file).execute_query()
#     print("'{0}' file has been downloaded into {1}".format(file.serverRelativeUrl, local_file.name))
