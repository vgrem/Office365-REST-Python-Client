"""
Retrieve a list of events in a my calendar.

https://learn.microsoft.com/en-us/graph/api/calendar-list-events?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
events = (
    client.me.calendar.events.get().top(100).select(["subject", "body"]).execute_query()
)
for event in events:
    print(event.subject)
