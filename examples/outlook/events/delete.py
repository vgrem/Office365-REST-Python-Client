"""
Deletes the event
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
event_id = "--event id goes here--"
event_to_del = client.me.calendar.events[event_id]
event_to_del.delete_object().execute_query()
