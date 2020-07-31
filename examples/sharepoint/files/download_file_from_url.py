import os
import tempfile

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File
from settings import settings

# where settings looks like
# settings = {
#     "user_credentials": {
#         "username": "username",
#         "password": "password"
#     },
#     "url": "https://company.sharepoint.com/",
#     "team": "my-team",
#     "file_path": "General/resolve_IP.bat"
# }


abs_file_url = "{site_url}sites/{team}/{file_path}".format(
                                                               site_url=settings.get('url'),
                                                               team=settings.get('team'),
                                                               file_path=settings.get('file_path')
                                                           )

user_credentials = UserCredential(settings.get('user_credentials').get('username'),
                                  settings.get('user_credentials').get('password'))


file_name = os.path.basename(abs_file_url)
with tempfile.TemporaryDirectory() as local_path:
    with open(os.path.join(local_path, file_name), 'wb') as local_file:
        file = File.from_url(abs_file_url).with_credentials(user_credentials).download(local_file).execute_query()
    print("'{0}' file has been downloaded into {1}".format(file.serverRelativeUrl, local_file.name))
