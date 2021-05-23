import os

from examples import acquire_token_by_client_credentials, test_user_principal_name
from office365.graph_client import GraphClient


client = GraphClient(acquire_token_by_client_credentials)

target_drive = client.users[test_user_principal_name].drive

local_path = "../../tests/data/SharePoint User Guide.docx"
with open(local_path, 'rb') as f:
    file_content = f.read()
file_name = os.path.basename(local_path)
target_file = target_drive.root.upload(file_name, file_content).execute_query()
print(f"File {target_file.web_url} has been uploaded")
