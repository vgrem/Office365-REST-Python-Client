"""
Demonstrates how to download a file content (intended for a small files with a size less than 4 Mb)
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "SitePages/Home.aspx"
file = ctx.web.lists.get_by_title("Site Pages").root_folder.files.get_by_url(
    "Home.aspx"
)
file_content = file.get_content().execute_query()
print("[Ok] file content has been downloaded")
