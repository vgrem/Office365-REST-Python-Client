"""
Get activities for a given user
https://learn.microsoft.com/en-us/graph/api/projectrome-get-activities?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
activities = client.me.activities.get().top(5).execute_query()
for activity in activities:
    print(activity)
