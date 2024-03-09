"""
Demonstrates how to upload a small file

https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
    test_user_principal_name_alt,
)

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
folder = client.users.get_by_principal_name(test_user_principal_name_alt).drive.root

# local_path = "../../data/Financial Sample.xlsx"
local_path = "../../data/countries.json"
# file = folder.upload_file(local_path).execute_query()
with open(local_path, "rb") as f:
    file = folder.upload_file(f).execute_query()
print("File {0} has been uploaded".format(file.web_url))
