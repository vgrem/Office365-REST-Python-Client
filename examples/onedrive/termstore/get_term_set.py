"""
Get term set by name
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
term_store = client.sites.root.term_store
group = term_store.groups.get_by_name("Geography").get().execute_query()
term_set = group.sets.get_by_name("Locations").get().execute_query()
print(term_set.id)
