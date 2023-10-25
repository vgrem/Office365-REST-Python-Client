"""
Get all the user's calendars

https://learn.microsoft.com/en-us/graph/api/user-list-calendars?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
calendars = client.me.calendars.top(10).get().execute_query()
for cal in calendars:
    print(cal)
