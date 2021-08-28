from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)

groups = client.groups.get().top(1).execute_query()
for cur_grp in groups:
    cur_grp.delete_object()
client.execute_batch()

