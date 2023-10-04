"""
Read list items from a default view
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
lib = ctx.web.default_document_library()
items = lib.default_view.get_items().execute_query()
for item in items:  # type: ListItem
    print(item.properties)
