"""
Demonstrates how to retrieve deleted items (of File type)
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
# result = ctx.web.default_document_library().get_changes(ChangeQuery(list_=False, item=True)).execute_query()
result = (
    ctx.web.recycle_bin.get().execute_query()
)  # filter("ItemType eq 1").execute_query()
for item in result:
    print(item.properties)
