from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)

groups = client.groups.get().top(100).execute_query()
deletedCount = 0
groups_count = len(groups)
while len(groups) > 0:
    cur_grp = groups[0]
    print(
        "({0} of {1}) Deleting {2} group ...".format(deletedCount + 1, groups_count, cur_grp.properties['displayName']))
    cur_grp.delete_object(permanent_delete=True).execute_query()
    print("Group deleted permanently.")
    deletedCount += 1
