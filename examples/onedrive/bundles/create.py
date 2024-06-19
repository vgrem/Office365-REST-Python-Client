"""
Create bundle

https://learn.microsoft.com/en-us/graph/api/drive-post-bundles?view=graph-rest-1.0&tabs=http#example-1-create-a-bundle
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
file_item = client.me.drive.root.get_by_path("Sample.html").get().execute_query()
bundle = client.me.drive.create_bundle(
    "Just some files", [file_item.id]
).execute_query()
print(bundle.web_url)
