"""
Search messages in a user's mailbox

https://learn.microsoft.com/en-us/graph/search-concept-messages
"""

import json

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
result = client.search.query_messages("Let's go for lunch").execute_query()
print(json.dumps(result.value.to_json(), indent=4))
