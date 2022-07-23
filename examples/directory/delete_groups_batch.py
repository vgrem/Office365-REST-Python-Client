from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)

result = client.groups.get_all().execute_query()
print("Total groups count (before): {0}".format(len(result)))

groups = client.groups.get().top(2).execute_query()
for cur_grp in groups:
    cur_grp.delete_object()
client.execute_batch()

result = client.groups.get_all().execute_query()
print("Total groups count (after): {0}".format(len(result)))

