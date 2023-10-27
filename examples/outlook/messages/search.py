"""
Search messages in a user's mailbox

https://learn.microsoft.com/en-us/graph/search-concept-messages
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
result = client.search.query_messages("Let's go for lunch").execute_query()
for item in result.value:
    for hit in item.hitsContainers[0].hits:
        print(hit.resource.properties.get("webLink"))
