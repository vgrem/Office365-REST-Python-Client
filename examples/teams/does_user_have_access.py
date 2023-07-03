"""
Determine whether a user has access to a shared channel.

https://learn.microsoft.com/en-us/graph/api/channel-doesuserhaveaccess?view=graph-rest-1.0&tabs=http
"""
import sys

from office365.graph_client import GraphClient
from office365.teams.team import Team
from tests import test_user_principal_name
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
teams = client.teams.top(1).get().execute_query()
if len(teams) < 1:
    sys.exit("No teams found")

team = teams[0]  # type: Team
result = team.primary_channel.does_user_have_access(user_principal_name=test_user_principal_name).execute_query()
print(result.value)

