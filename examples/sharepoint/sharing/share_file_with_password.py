"""
Share a file with a password
"""
import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from office365.sharepoint.sharing.role_type import RoleType
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file_url = "Shared Documents/SharePoint User Guide.docx"
target_file = ctx.web.get_file_by_server_relative_url(file_url)
result = target_file.share_link(
    SharingLinkKind.Flexible, role=RoleType.Editor, password="password"
).execute_query()

# print(json.dumps(result.value.to_json(), indent=4))
print("Shared link url: {0}".format(result.value.sharingLinkInfo))
