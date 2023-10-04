import json

from examples.sharepoint import upload_sample_file
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
remote_file = upload_sample_file(ctx, "../../data/Financial Sample.xlsx")
result = remote_file.share_link(SharingLinkKind.OrganizationView).execute_query()
print(json.dumps(result.value.to_json(), indent=4))
