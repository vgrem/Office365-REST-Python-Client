"""
Create bundle

https://learn.microsoft.com/en-us/graph/api/drive-post-bundles?view=graph-rest-1.0&tabs=http#example-1-create-a-bundle
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
file_item = client.me.drive.root.get_by_path("Sample.html").get().execute_query()
bundle = client.me.drive.create_bundle("Just some files", [file_item.id]).execute_query()
print(bundle.web_url)
