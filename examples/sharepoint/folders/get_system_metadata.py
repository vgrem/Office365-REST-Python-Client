"""
Retrieves folder system metadata
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folder_url = "Shared Documents/Archive"

folder_item = (
    ctx.web.get_folder_by_server_relative_url(folder_url)
    .list_item_all_fields.get()
    .execute_query()
)
author = (
    ctx.web.site_users.get_by_id(folder_item.get_property("AuthorId"))
    .get()
    .execute_query()
)
print(author)
