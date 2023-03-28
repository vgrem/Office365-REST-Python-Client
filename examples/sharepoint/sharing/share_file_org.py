import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file_url = "/sites/team/Shared Documents/SharePoint User Guide.docx"
target_file = ctx.web.get_file_by_server_relative_url(file_url)
result = target_file.share_link(SharingLinkKind.OrganizationView).execute_query()
print(json.dumps(result.value.to_json(), indent=4))
