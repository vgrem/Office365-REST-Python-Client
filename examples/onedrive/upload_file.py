import os

from examples import acquire_token_by_client_credentials, sample_user_principal_name_alt
from office365.graph_client import GraphClient


client = GraphClient(acquire_token_by_client_credentials)

remote_drive = client.users[sample_user_principal_name_alt].drive.root.get_by_path("archive")

local_path = "../../tests/data/SharePoint User Guide.docx"
# local_path = "../data/countries.json"
with open(local_path, 'rb') as f:
    file_content = f.read()
file_name = os.path.basename(local_path)
remote_file = remote_drive.upload(file_name, file_content).execute_query()
print(f"File {remote_file.web_url} has been uploaded")
