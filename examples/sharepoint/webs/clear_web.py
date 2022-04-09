from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.list import List
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

lists = ctx.web.lists.filter("Hidden eq false and IsCatalog eq false").get().execute_query()
for lo in lists:  # type: List
    lo.delete_object().execute_query()
    print("List: {0} has been deleted".format(lo.title))
