"""
Shares a folder
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.external_site_option import ExternalSharingSiteOption
from tests import test_team_site_url, test_user_credentials, test_user_principal_name

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
folder_url = "Shared Documents/Archive"
folder = ctx.web.get_folder_by_server_relative_path(folder_url)
result = folder.list_item_all_fields.share(
    test_user_principal_name, ExternalSharingSiteOption.View
).execute_query()
print(result.url)
