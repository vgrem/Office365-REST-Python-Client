"""
Gets folders from drive
https://learn.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_password,
    test_team_site_url,
    test_tenant,
    test_username,
)

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
# items = client.me.drive.root.get_files(False).execute_query()
site = client.sites.get_by_url(test_team_site_url)
items = (
    site.lists["Documents_Archive"].drive.root.get_folders(False, 10000).execute_query()
)
print("{0} folders found".format(len(items)))
# for folder_item in items:
#    print(folder_item.web_url)
