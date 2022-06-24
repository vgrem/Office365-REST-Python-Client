from pprint import pprint

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = '/sites/team/Shared Documents/big_buck_bunny.mp4'
file = ctx.web.get_file_by_server_relative_url(file_url)
file_item = file.listItemAllFields.select(["EffectiveBasePermissions"]).get().execute_query()  # type: ListItem
print(file_item.effective_base_permissions.permission_levels)

