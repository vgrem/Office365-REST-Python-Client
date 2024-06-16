"""
Export Term Store
"""
import json

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

store = ctx.taxonomy.term_store
term_groups = ctx.taxonomy.term_store.term_groups.get().execute_query()
for term_group in term_groups:
    term_sets = term_group.term_sets.get().execute_query()
print(json.dumps(term_groups.to_json(), indent=4))
