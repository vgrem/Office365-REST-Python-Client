import json

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from tests import test_team_site_url

client = GraphClient(acquire_token_by_client_credentials)
term_sets = client.sites.get_by_url(test_team_site_url).term_store.get_all_term_sets().execute_query()
term_sets_json = [ts.properties for ts in term_sets]
print(json.dumps(term_sets_json))
