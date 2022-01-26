from pprint import pprint

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

file_url = "https://mediadev8.sharepoint.com/:w:/s/team/Ed_R46Jt0Y5GidJ8yhCBLG4BEmn1aHJzXF2442_NvrPuag?e=aPujrl"

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
result = ctx.web.get_sharing_link_data(file_url).execute_query()

file = ctx.web.get_file_by_id(result.value.ObjectUniqueId).execute_query()
pprint(result.value)
