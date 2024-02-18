from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

term_group_name = "Geography"

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
term_group = ctx.taxonomy.term_store.term_groups.get_by_name(
    term_group_name
).execute_query()
print(term_group)
