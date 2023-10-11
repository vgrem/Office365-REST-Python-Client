from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
view = ctx.web.default_document_library().views.get_by_title("All Documents")
items = view.get_items().expand(["Author"]).execute_query()
for item in items:  # type: ListItem
    print(item.properties)
