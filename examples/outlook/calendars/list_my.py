"""
Get all the user's calendars

https://learn.microsoft.com/en-us/graph/api/user-list-calendars?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
calendars = client.me.calendars.top(10).get().execute_query()
for cal in calendars:
    print(cal)
