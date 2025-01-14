"""
Retrieve the metadata for a driveItem (folder facet) in a drive

https://learn.microsoft.com/en-us/graph/api/driveitem-get?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
folder_item = client.me.drive.root.get_by_path("archive/2018").get().execute_query()
print("Folder url {0}".format(folder_item.web_url))
