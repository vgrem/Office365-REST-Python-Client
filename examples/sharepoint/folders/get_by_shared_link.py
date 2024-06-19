"""
Returns the folder object from the tokenized sharing link URL.
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

folder = ctx.web.get_folder_by_server_relative_url("Shared Documents/Archive")
# Share a folder
result = folder.share_link(SharingLinkKind.OrganizationView).execute_query()


shared_folder = ctx.web.get_folder_by_guest_url(str(result.value)).execute_query()
print(shared_folder)
