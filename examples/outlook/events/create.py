"""
Create an event in the current user's default calendar

https://learn.microsoft.com/en-us/graph/api/user-post-events?view=graph-rest-1.0
"""

from datetime import datetime, timedelta

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

when = datetime.utcnow() + timedelta(days=1)
client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
new_event = client.me.calendar.events.add(
    subject="Let's go for lunch",
    body="Does mid month work for you?",
    start=when,
    end=when + timedelta(hours=1),
    attendees=["samanthab@contoso.onmicrosoft.com"],
).execute_query()
print("Event created")
