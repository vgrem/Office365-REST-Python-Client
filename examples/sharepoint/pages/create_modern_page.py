import sys

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.publishing.site_page import SitePage
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
new_page = ctx.site_pages.pages.add()
result = new_page.save_draft(title="Latest News 123").execute_query()
if result.value is False:
    pass
    #new_page.delete_object().execute_query()
    #sys.exit("[Error] An error occurred while saving a page...")
new_page.publish().execute_query()

pages = ctx.site_pages.pages.get().execute_query()
for page in pages:  # type: SitePage
    print(page.file_name)
