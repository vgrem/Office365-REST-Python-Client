from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
ctx.web.lists.get_by_title("Tasks").save_as_template("Tasks.stp", "Tasks", "", True).execute_query()
