from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "/sites/team/Shared Documents/SharePoint User Guide.docx"
version = ctx.web.get_file_by_server_relative_path(file_url).versions.get_by_id(1).expand(["CreatedBy"]).get().execute_query()
print(version.created_by.login_name)
