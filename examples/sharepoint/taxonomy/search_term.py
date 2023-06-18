from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.terms.term import Term
from tests import test_team_site_url, test_client_credentials

term_name = "Sweden"

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
terms = ctx.taxonomy.term_store.search_term(term_name).execute_query()
for term in terms:  # type: Term
    print(term.labels[0])
