from pprint import pprint

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.permissions.kind import PermissionKind
from tests import test_team_site_url, test_user_principal_name_alt, test_user_credentials

client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file_url = "/sites/team/Shared Documents/report #123.csv"

# user = client.web.site_users.get_by_email(test_user_principal_name_alt).get().execute_query()
target_user = client.web.site_users.get_by_email(test_user_principal_name_alt)
target_file = client.web.get_file_by_server_relative_path(file_url)
result = target_file.listItemAllFields.get_user_effective_permissions(target_user).execute_query()
pprint(result.value.permission_levels)  # print all permission levels

# verify whether user has Reader role to a file
if result.value.has(PermissionKind.OpenItems):
    print("User has access to read a file")

