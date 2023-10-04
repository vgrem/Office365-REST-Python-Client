from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.publishing.pages.page import SitePage
from tests import test_client_credentials, test_site_url

ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)

site_pages = ctx.site_pages.pages.get().execute_query()
for site_page in site_pages:  # type: SitePage
    print(site_page.file_name)
