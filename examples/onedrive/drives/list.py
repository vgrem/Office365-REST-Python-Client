"""
List available drives

https://learn.microsoft.com/en-us/graph/api/drive-list?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
drives = client.drives.get().top(10).execute_query()
for drive in drives:
    print("Drive url: {0}".format(drive.web_url))
