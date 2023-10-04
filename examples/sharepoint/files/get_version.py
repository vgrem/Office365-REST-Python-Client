"""
Retrieves versions of the file
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.versions.version import FileVersion
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "SitePages/Home.aspx"
file_with_versions = (
    ctx.web.get_file_by_server_relative_path(file_url)
    .expand(["Versions"])
    .get()
    .execute_query()
)
for version in file_with_versions.versions:  # type: FileVersion
    print(version.version_label)
