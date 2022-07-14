from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.calendar.event import Event

client = GraphClient(acquire_token_by_username_password)
events = client.me.calendar.events.get().top(10).execute_query()
for event in events:  # type: Event
    print(event.subject)
