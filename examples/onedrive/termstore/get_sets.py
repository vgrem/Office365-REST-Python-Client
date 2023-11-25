"""
Get term sets in Group
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
term_store = client.sites.root.term_store
sets = term_store.groups.get_by_name("Geography").sets.get().execute_query()
# term_set = group.sets.get_by_name("Locations").get().execute_query()
for ts in sets:
    print(ts)
