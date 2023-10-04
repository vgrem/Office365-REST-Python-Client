"""
Calculate and list the documents that a user has viewed or modified.

https://learn.microsoft.com/en-us/graph/api/insights-list-used?view=graph-rest-1.0&tabs=http
"""
import json

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
result = client.me.insights.used.get().execute_query()
print(json.dumps(result.to_json(), indent=4))
