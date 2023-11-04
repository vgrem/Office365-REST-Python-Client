"""
Demonstrates how to update folder properties
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

folder_url = "Shared Documents/Archive"
folder = ctx.web.get_folder_by_server_relative_path(folder_url)
folder_item = folder.list_item_all_fields
prop_name = "DocScope"
prop_value = "Public"
folder_item.set_property(prop_name, prop_value).update().execute_query()
