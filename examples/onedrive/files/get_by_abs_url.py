"""
Retrieves file by absolute url
"""
from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_password,
    test_team_site_url,
    test_tenant,
    test_username,
)

file_abs_url = "{0}/Shared Documents/Financial Sample.csv".format(test_team_site_url)

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)

# csv_file = client.me.drive.root.upload_file("../../data/Financial Sample.csv").execute_query()

file_item = client.shares.by_url(file_abs_url).drive_item.get().execute_query()

result = file_item.get_content().execute_query()
print(result.value)
