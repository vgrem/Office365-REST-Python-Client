from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

# Generate sharing link url for a file first
file = ctx.web.get_file_by_server_relative_url(
    "/sites/team/SitePages/How To Use This Library.aspx"
)
# Share a file
result = file.share_link(SharingLinkKind.OrganizationView).execute_query()

# Resolve file by sharing link url (guest url)
guest_url = result.value.sharingLinkInfo.Url
shared_file = ctx.web.get_file_by_guest_url(guest_url).execute_query()
print(shared_file.name)
