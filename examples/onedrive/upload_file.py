import os

import msal

from office365.graph_client import GraphClient
from settings import settings


def acquire_token():
    """
    Acquire token (MSAL)
    """
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings.get('tenant'))
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=settings.get('client_credentials').get('client_id'),
        client_credential=settings.get('client_credentials').get('client_secret')
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result


client = GraphClient(acquire_token)
user_name = settings.get('test_account_name')
target_drive = client.users[user_name].drive

local_path = "../../tests/data/SharePoint User Guide.docx"
with open(local_path, 'rb') as f:
    file_content = f.read()
file_name = os.path.basename(local_path)
target_file = target_drive.root.upload(file_name, file_content).execute_query()
print(f"File {target_file.web_url} has been uploaded")
