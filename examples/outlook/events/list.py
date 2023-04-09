from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.calendar.events.event import Event

client = GraphClient(acquire_token_by_username_password)
events = client.me.calendar.events.get_all().select(["subject", "body"]).execute_query()
for event in events:  # type: Event
    print(event.subject)
