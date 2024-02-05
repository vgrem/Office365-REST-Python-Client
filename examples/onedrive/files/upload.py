"""
Demonstrates how to upload a small file

https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_user_principal_name_alt
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
folder = client.users.get_by_principal_name(test_user_principal_name_alt).drive.root

local_path = "../../data/Financial Sample.xlsx"
file = folder.upload_file(local_path).execute_query()
print(f"File {file.web_url} has been uploaded")
