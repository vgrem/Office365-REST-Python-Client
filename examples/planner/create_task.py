from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)
my_tasks = client.me.planner.tasks.get().execute_query()
task = client.planner.tasks.add(title="Update client list").execute_query()
print(my_tasks)


