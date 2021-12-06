from datetime import datetime, timedelta

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.calendar.event import Event

client = GraphClient(acquire_token_by_username_password)
new_event = client.me.calendar.events.add()  # type: Event
new_event.subject = "Let's go for lunch"
new_event.body = "Does mid month work for you?"
new_event.start = datetime.utcnow() + timedelta(days=1)
new_event.end = datetime.utcnow() + timedelta(days=1) + timedelta(hours=1)
new_event.attendees = ["samanthab@contoso.onmicrosoft.com"]
client.execute_query()
print("Event created")
