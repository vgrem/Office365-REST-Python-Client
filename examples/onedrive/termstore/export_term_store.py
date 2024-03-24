"""
Demonstrates how to retrieve a flat list of all TermSet objects
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_team_site_url, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
term_sets = (
    client.sites.get_by_url(test_team_site_url)
    .term_store.get_all_term_sets()
    .execute_query()
)
names = [ts.localized_names[0].name for ts in term_sets]
print(names)
