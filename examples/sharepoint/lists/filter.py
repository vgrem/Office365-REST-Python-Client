from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
result = (
    ctx.web.lists.get()
    .select(["IsSystemList", "Title"])
    .filter("IsSystemList eq true")
    .execute_query()
)
for lst in result:  # type: List
    print(lst.title)
