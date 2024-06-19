"""
List available drives

https://learn.microsoft.com/en-us/graph/api/drive-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
drives = client.drives.get().top(100).execute_query()
for drive in drives:
    print("Drive url: {0}".format(drive.web_url))
