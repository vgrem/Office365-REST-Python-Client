from office365.graph_client import GraphClient
from tests import test_team_site_url
from tests.graph_case import acquire_token_by_username_password

file_abs_url = "{0}/Shared Documents/big_buck_bunny.mp4".format(test_team_site_url)

client = GraphClient(acquire_token_by_username_password)
file_item = client.shares.by_url(file_abs_url).drive_item.get().execute_query()
print(f"Drive item Id: {file_item.id}")
