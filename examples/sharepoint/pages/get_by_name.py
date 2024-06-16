"""
Get site page by name
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
site_page = ctx.site_pages.pages.get_by_name("Home.aspx").execute_query()
print(site_page)
