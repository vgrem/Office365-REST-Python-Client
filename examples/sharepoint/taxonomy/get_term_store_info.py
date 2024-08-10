from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
term_store = ctx.taxonomy.term_store.get().execute_query()
print(term_store)
