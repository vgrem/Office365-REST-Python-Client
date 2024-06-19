"""
Retrieves a collection of DriveItem resources that have been shared with the current user

https://learn.microsoft.com/en-us/graph/api/drive-sharedwithme?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
drive_items = client.me.drive.shared_with_me().execute_query()
for item in drive_items:
    print("Drive Item url: {0}".format(item.web_url))
