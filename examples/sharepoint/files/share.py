"""
Creates a sharing link for a file based on the specified parameters and optionally
sends an email to the people that are listed in the specified parameters
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file_url = "Shared Documents/SharePoint User Guide.docx"
result = (
    ctx.web.get_file_by_server_relative_path(file_url)
    .share_link(SharingLinkKind.AnonymousView)
    .execute_query()
)
print(result.value.sharingLinkInfo)
