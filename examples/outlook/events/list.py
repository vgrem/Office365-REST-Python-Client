"""
Retrieve a list of events in a my calendar.

https://learn.microsoft.com/en-us/graph/api/calendar-list-events?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
events = (
    client.me.calendar.events.get().top(10).select(["subject", "body"]).execute_query()
)
for event in events:
    print(event.subject)
