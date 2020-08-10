import os
import tempfile

from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.files.file import File

root_site_url = settings.get('url')
client_credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                                      settings.get('client_credentials').get('client_secret'))

abs_file_url = "{site_url}sites/team/Shared Documents/big_buck_bunny.mp4".format(site_url=root_site_url)
with tempfile.TemporaryDirectory() as local_path:
    file_name = os.path.basename(abs_file_url)
    with open(os.path.join(local_path, file_name), 'wb') as local_file:
        file = File.from_url(abs_file_url).with_credentials(client_credentials).download(local_file).execute_query()
    print("'{0}' file has been downloaded into {1}".format(file.serverRelativeUrl, local_file.name))
