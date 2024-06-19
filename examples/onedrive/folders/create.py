"""
Create a new folder in a drive

https://learn.microsoft.com/en-us/graph/api/driveitem-post-children?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import create_unique_name, test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
lib = client.sites.root.lists["Documents"]
folder_name = create_unique_name("Archive")
folder_item = lib.drive.root.create_folder(folder_name).execute_query()
