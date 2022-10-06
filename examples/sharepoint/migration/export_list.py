from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
ctx.web.lists.get_by_title("Site Pages").save_as_template("SitePages.stp", "Site Pages", "", True).execute_query()
