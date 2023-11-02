"""
Retrieves file system metadata
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "SitePages/Home.aspx"
file = (
    ctx.web.get_file_by_server_relative_url(file_url)
    .expand(["ModifiedBy", "Author", "TimeCreated", "TimeLastModified"])
    .get()
    .execute_query()
)

print(file.author)
print(file.modified_by)
print(file.time_created)
print(file.time_last_modified)
