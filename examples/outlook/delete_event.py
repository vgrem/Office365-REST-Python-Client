from datetime import datetime, timedelta

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.calendar.event import Event

client = GraphClient(acquire_token_by_username_password)
event_id = '--event id goes here--'
event_to_del = client.me.calendar.events[event_id]  # type: Event
event_to_del.delete_object().execute_query()
