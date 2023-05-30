"""
Delete group

Notes:

    - Group.delete_object() Microsoft 365 groups are moved to a temporary container and can be restored within 30 days
    - Group.delete_object(permanent_delete=True) Microsoft 365 permanently deleted

https://learn.microsoft.com/en-us/graph/api/group-delete?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
groups = client.groups.get().top(1).execute_query()
deletedCount = 0
groups_count = len(groups)
while len(groups) > 0:
    cur_grp = groups[0]
    print(
        "({0} of {1}) Deleting {2} group ...".format(deletedCount + 1, groups_count, cur_grp.properties['displayName']))
    cur_grp.delete_object(permanent_delete=True).execute_query()
    print("Group deleted permanently.")
    deletedCount += 1
