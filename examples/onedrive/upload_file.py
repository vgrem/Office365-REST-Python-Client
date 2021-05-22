import os

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from tests import settings

client = GraphClient(acquire_token_by_client_credentials)
user_name = settings.get('first_account_name')
target_drive = client.users[user_name].drive

local_path = "../../tests/data/SharePoint User Guide.docx"
with open(local_path, 'rb') as f:
    file_content = f.read()
file_name = os.path.basename(local_path)
target_file = target_drive.root.upload(file_name, file_content).execute_query()
print(f"File {target_file.web_url} has been uploaded")
