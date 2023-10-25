"""
Retrieves a collection of DriveItem resources that have been shared with the current user

https://learn.microsoft.com/en-us/graph/api/drive-sharedwithme?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
drive_items = client.me.drive.shared_with_me().execute_query()
for item in drive_items:
    print("Drive Item url: {0}".format(item.web_url))
