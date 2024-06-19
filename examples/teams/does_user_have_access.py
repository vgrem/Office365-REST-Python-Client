"""
Determine whether a user has access to a shared channel.

https://learn.microsoft.com/en-us/graph/api/channel-doesuserhaveaccess?view=graph-rest-1.0
"""

import sys

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
    test_user_principal_name,
)

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
teams = client.teams.top(1).get().execute_query()
if len(teams) < 1:
    sys.exit("No teams found")

team = teams[0]
result = team.primary_channel.does_user_have_access(
    user_principal_name=test_user_principal_name
).execute_query()
print(result.value)
