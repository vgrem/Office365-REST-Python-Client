"""
Demonstrates how to rename a page
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

from_url = "Home_Archive.aspx"
to_url = "Home.aspx"
ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file = ctx.web.lists.get_by_title("Site Pages").root_folder.files.get_by_url(from_url)
file.rename(to_url).execute_query()
