"""
Get activities for a given user
https://learn.microsoft.com/en-us/graph/api/projectrome-get-activities?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
activities = client.me.activities.get().top(5).execute_query()
for activity in activities:
    print(activity)
