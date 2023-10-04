import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.groups.group import TermGroup
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

store = ctx.taxonomy.term_store.get().execute_query()

term_groups = ctx.taxonomy.term_store.term_groups.get_all().execute_query()
for term_group in term_groups:  # type: TermGroup
    term_sets = term_group.term_sets.get_all().execute_query()
    print(json.dumps(term_sets.to_json(), indent=4))
