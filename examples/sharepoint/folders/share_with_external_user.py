"""
Share a Folder with External User
"""

import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.role_type import RoleType
from office365.sharepoint.sharing.user_role_assignment import UserRoleAssignment
from tests import test_team_site_url, test_client_credentials, test_user_principal_name_alt

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folder_url = "Shared Documents/Archive"
folder = ctx.web.get_folder_by_server_relative_path(folder_url)
assignment = UserRoleAssignment(RoleType.Guest, test_user_principal_name_alt)
result = folder.update_document_sharing_info([assignment]).execute_query()
print(json.dumps(result.value.to_json(), indent=4))
