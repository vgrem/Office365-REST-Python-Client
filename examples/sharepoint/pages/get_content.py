"""
Get site page content
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
page = ctx.site_pages.pages.get_by_name("Home.aspx").execute_query()
print(page.canvas_content)
print(page.layout_web_parts_content)
