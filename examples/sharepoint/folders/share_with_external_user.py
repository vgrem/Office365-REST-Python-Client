"""
Share a folder with a set of users
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.role import Role
from office365.sharepoint.sharing.user_role_assignment import UserRoleAssignment
from tests import (
    test_client_credentials,
    test_team_site_url,
    test_user_principal_name_alt,
)

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folder_url = "Shared Documents/Archive"
folder = ctx.web.get_folder_by_server_relative_path(folder_url)
assignment = UserRoleAssignment(Role.Edit, test_user_principal_name_alt)
result = folder.update_document_sharing_info([assignment]).execute_query()
for item in result.value:
    print(item)
