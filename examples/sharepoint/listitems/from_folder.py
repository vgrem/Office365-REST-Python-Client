from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery
from tests import test_client_credentials, test_team_site_url


def create_custom_query():
    qry = CamlQuery()
    qry.FolderServerRelativeUrl = "Shared Documents/Archive"
    return qry


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
lib = ctx.web.lists.get_by_title("Documents")
result = lib.get_items(create_custom_query()).execute_query()
for item in result:
    print(item.properties)
