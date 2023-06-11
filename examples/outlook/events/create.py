"""
Create an event in the current user's default calendar

https://learn.microsoft.com/en-us/graph/api/user-post-events?view=graph-rest-1.0&tabs=http
"""

from datetime import datetime, timedelta
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

when = datetime.utcnow() + timedelta(days=1)
client = GraphClient(acquire_token_by_username_password)
new_event = client.me.calendar.events.add(
    subject="Let's go for lunch",
    body="Does mid month work for you?",
    start=when,
    end=when + timedelta(hours=1),
    attendees=["samanthab@contoso.onmicrosoft.com"]
).execute_query()
print("Event created")
