# Example: share a Document with External User

import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.document_manager import DocumentSharingManager
from office365.sharepoint.sharing.role_type import RoleType
from office365.sharepoint.sharing.user_role_assignment import UserRoleAssignment
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
folder_url = "/".join([test_team_site_url, "Shared Documents"])
assignment = UserRoleAssignment(RoleType.Guest, "jdoe@contoso.com")
result = DocumentSharingManager.update_document_sharing_info(ctx, folder_url, [assignment],
                                                             send_server_managed_notification=True).execute_query()
print(json.dumps(result.value.to_json(), indent=4))
