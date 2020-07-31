# example that downloads file test.pdf from document library with name "Software".
# Current example uses App authentication. See examples "connect_with_app.py"
# For detailed info read official Microsoft article: Granting access using SharePoint App-Only

import os
import tempfile
import time

from office365.sharepoint.files.file import File
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

site_url = "https://company.sharepoint.com/sites/my-team/"
app_principal = {
    'client_id': 'client ID',
    'client_secret': 'client Secret',
}

context_auth = AuthenticationContext(url=site_url)
context_auth.acquire_token_for_app(client_id=app_principal['client_id'], client_secret=app_principal['client_secret'])

abs_file_url = site_url + "Software/test.pdf"
ctx = ClientContext(site_url, context_auth)
file_name = os.path.basename(abs_file_url)

with tempfile.TemporaryDirectory() as local_path:
    with open(os.path.join(local_path, file_name), 'wb') as local_file:
        file = File.from_url(abs_file_url).with_context(ctx).download(local_file).execute_query()
    print("'{0}' file has been downloaded into {1}".format(file.serverRelativeUrl, local_file.name))

    # give some time before delete file :)
    time.sleep(100)
