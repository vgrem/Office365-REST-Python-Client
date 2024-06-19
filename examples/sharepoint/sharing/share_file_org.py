"""
Creates a tokenized sharing link for a file
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file = ctx.web.get_file_by_server_relative_url("Shared Documents/Financial Sample.xlsx")
result = file.share_link(SharingLinkKind.OrganizationView).execute_query()
print("Shared link url: {0}".format(result.value.sharingLinkInfo))
