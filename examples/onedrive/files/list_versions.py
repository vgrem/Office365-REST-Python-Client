"""
List versions of a driveItem

https://learn.microsoft.com/en-us/graph/api/driveitem-list-versions?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
file_item = (
    client.sites.root.drive.root.get_by_path("Financial Sample.xlsx")
    .expand(["versions"])
    .get()
    .execute_query()
)
for ver in file_item.versions:
    print(ver.id)
