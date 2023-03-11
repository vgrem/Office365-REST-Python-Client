from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

file_url = "/sites/team/SitePages/Home_Archive.aspx"
ctx.web.get_file_by_server_relative_url(file_url).rename("Home_Archive2.aspx").execute_query()

