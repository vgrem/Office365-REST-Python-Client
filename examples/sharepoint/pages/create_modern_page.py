import uuid

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.publishing.pages.page import SitePage
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
page_title = "Site Page {0}".format(uuid.uuid4().hex)
new_page = ctx.site_pages.pages.add()
new_page.save_draft(title=page_title)
new_page.publish().execute_query()

pages = ctx.site_pages.pages.get().execute_query()
for page in pages:  # type: SitePage
    print(page.file_name)
