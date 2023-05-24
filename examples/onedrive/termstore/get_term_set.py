from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)
term_store = client.sites.root.term_store
group = term_store.groups.get_by_name("Geography").get().execute_query()
print(group.id)
