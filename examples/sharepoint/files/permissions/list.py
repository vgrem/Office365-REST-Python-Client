from pprint import pprint

from office365.sharepoint.client_context import ClientContext
from tests import (
    test_team_site_url,
    test_user_credentials,
    test_user_principal_name_alt,
)

client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file_url = "Shared Documents/Financial Sample.xlsx"

target_user = client.web.site_users.get_by_email(test_user_principal_name_alt)
target_file = client.web.get_file_by_server_relative_path(file_url)
result = target_file.listItemAllFields.get_user_effective_permissions(
    target_user
).execute_query()
pprint(result.value.permission_levels)  # print all permission levels
