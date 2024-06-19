"""
Delete group

Notes:

    - Group.delete_object() Microsoft 365 groups are moved to a temporary container and can be restored within 30 days
    - Group.delete_object(permanent_delete=True) Microsoft 365 permanently deleted

https://learn.microsoft.com/en-us/graph/api/group-delete?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
groups = client.groups.get().top(10).execute_query()
deletedCount = 0
groups_count = len(groups)
while len(groups) > 0:
    cur_grp = groups[0]
    print(
        "({0} of {1}) Deleting {2} group ...".format(
            deletedCount + 1, groups_count, cur_grp.display_name
        )
    )
    cur_grp.delete_object(permanent_delete=True).execute_query()
    print("Group deleted permanently.")
    deletedCount += 1
