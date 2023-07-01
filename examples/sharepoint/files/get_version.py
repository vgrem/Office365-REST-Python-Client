"""
Retrieves versions of the file
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.versions.version import FileVersion
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "SitePages/Home.aspx"
file = ctx.web.get_file_by_server_relative_path(file_url)
#versions = file.versions.expand(["CreatedBy"]).get().execute_query()
file_with_versions = file.expand(["Versions"])  # retrieve file along with versions
ctx.load(file_with_versions)
ctx.execute_query()
for version in file_with_versions.versions:  # type: FileVersion
    print(version.version_label)
    #print(version.created_by.login_name)
