"""
Returns a link for downloading the file without authentication.
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "Shared Documents/Financial Sample.xlsx"

result = (
    ctx.web.get_file_by_server_relative_path(file_url)
    .get_pre_authorized_access_url(1)
    .execute_query()
)
print(result.value)
