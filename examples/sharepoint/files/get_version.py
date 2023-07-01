"""
Retrieves versions of the file
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.versions.version import FileVersion
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "Shared Documents/SharePoint User Guide.docx"
versions = ctx.web.get_file_by_server_relative_path(file_url).versions.expand(["CreatedBy"]).get().execute_query()
for version in versions:  # type: FileVersion
    print(version.created_by.login_name)
