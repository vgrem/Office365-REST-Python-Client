"""
Demonstrates how to rename a page
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

file_url = "Site Pages/Home.aspx"
new_name = "NewHome.aspx"
ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file = ctx.web.get_file_by_server_relative_path(file_url)
file.rename(new_name).execute_query()
