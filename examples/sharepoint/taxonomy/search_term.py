"""
Search term by name
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

term_name = "Sweden"

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
terms = ctx.taxonomy.term_store.search_term(term_name).execute_query()
for term in terms:
    print(term.labels[0])
