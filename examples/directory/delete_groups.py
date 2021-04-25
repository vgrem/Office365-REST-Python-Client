from examples import acquire_token_client_credentials
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_client_credentials)

groups = client.groups.get().top(10).execute_query()
index = 0
groups_count = len(groups)
while len(groups) > 0:
    cur_grp = groups[0]
    print("({0} of {1}) Deleting {2} group ...".format(index + 1, groups_count, cur_grp.properties['displayName']))
    cur_grp.delete_object().execute_query()
    print("Group deleted.")
    index += 1

deleted_groups = client.directory.deleted_groups.get().execute_query()
groups_count = len(deleted_groups)
index = 0
while len(deleted_groups) > 0:
    cur_grp = deleted_groups[0]
    print("({0} of {1}) Deleting {2} group permanently ...".format(index + 1, groups_count,
                                                                   cur_grp.properties['displayName']))
    cur_grp.delete_object().execute_query()
    print("Group deleted.")
    index += 1
