"""
Delete groups in batch mode

https://learn.microsoft.com/en-us/graph/api/group-delete?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)

result = client.groups.get_all().execute_query()
print("Total groups count (before): {0}".format(len(result)))

groups = client.groups.get().top(4).execute_query()
for cur_grp in groups:
    cur_grp.delete_object()
client.execute_batch()
print("Groups have been deleted")

result = client.groups.get_all().execute_query()
print("Total groups count (after): {0}".format(len(result)))
