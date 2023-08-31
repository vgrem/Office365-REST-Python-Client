"""
Create a single-value extended property for a message

Demonstrates how to create one single-value extended property for the specified existing message.

https://learn.microsoft.com/en-us/graph/api/singlevaluelegacyextendedproperty-post-singlevalueextendedproperties?view=graph-rest-1.0
"""
import sys

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.top(1).get().execute_query()
if len(messages) == 0:
    sys.exit("No messages were found")


message = messages[0].add_extended_property("Color", "Green").update().execute_query()
print(message.web_link)
