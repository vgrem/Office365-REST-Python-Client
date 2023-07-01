"""
Retrieves the permissions on the file that are assigned to the current user.
"""
from pprint import pprint

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = 'Shared Documents/big_buck_bunny.mp4'
file = ctx.web.get_file_by_server_relative_url(file_url)
file_item = file.listItemAllFields.select(["EffectiveBasePermissions"]).get().execute_query()
pprint(file_item.effective_base_permissions.permission_levels)

