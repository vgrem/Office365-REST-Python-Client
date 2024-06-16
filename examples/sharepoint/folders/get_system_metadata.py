"""
Retrieves folder system metadata
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_title = "Docs"

folder_items = (
    ctx.web.lists.get_by_title(list_title)
    .items.filter("FSObjType eq 1")
    .select(
        [
            "FSObjType",
            "Author/Id",
            "Author/Title",
            "Author/Name",
            "Editor/Id",
            "Editor/Title",
            "Editor/Name",
        ]
    )
    .expand(["Author", "Editor"])
    .get()
    .execute_query()
)

folder_path = "Archive"  # folder relative path
folder_item = (
    ctx.web.lists.get_by_title(list_title)
    .get_item_by_url(folder_path)
    .select(
        [
            "Author/Id",
            "Author/Title",
            "Author/Name",
            "Editor/Id",
            "Editor/Title",
            "Editor/Name",
        ]
    )
    .expand(["Author", "Editor"])
    .get()
    .execute_query()
)

print(folder_item.properties.get("Author"))
print(folder_item.properties.get("Editor"))
