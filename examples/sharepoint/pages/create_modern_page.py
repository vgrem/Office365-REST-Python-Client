from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.publishing.site_page import SitePage
from office365.sharepoint.publishing.site_page_service import SitePageService
from tests import  test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
site_pages_svc = SitePageService(ctx)
draft_page = site_pages_svc.pages.add().save_draft(title="Latest News").execute_query()

pages = site_pages_svc.pages.get().execute_query()
for page in pages:  # type: SitePage
    print(page.file_name)
