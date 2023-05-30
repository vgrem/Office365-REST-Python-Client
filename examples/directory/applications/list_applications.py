"""
Get the list of applications in this organization
https://learn.microsoft.com/en-us/graph/api/application-list?view=graph-rest-1.0&tabs=http
"""
import json

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
apps = client.applications.get().top(10).execute_query()
names = [app.display_name for app in apps]
print(json.dumps(names, indent=4))
