from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

target_folder_url = "/Shared Documents/Archive/2022/09/01"
target_folder = ctx.web.default_document_library().root_folder.folders.ensure_folder_path("Archive/2022/09")
folder_item = target_folder.list_item_all_fields
folder_item.set_property("DocScope", "Public").update().execute_query()
print(target_folder.serverRelativeUrl)
