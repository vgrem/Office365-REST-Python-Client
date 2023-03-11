from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

target_list = ctx.web.lists.get_by_title("Site Pages").get().execute_query()
print("List title: {0}".format(target_list.title))
