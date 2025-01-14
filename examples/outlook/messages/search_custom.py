"""
Search messages in a user's mailbox

https://learn.microsoft.com/en-us/graph/search-concept-messages
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
result = client.search.query_messages(
    "Meet for lunch?", page_from=1, size=10
).execute_query()
for item in result.value:
    for hit in item.hitsContainers[0].hits:
        print(hit.resource.get_property("webLink"))
