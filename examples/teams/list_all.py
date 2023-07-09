"""
List all teams in an organization (tenant)

https://learn.microsoft.com/en-us/graph/teams-list-all-teams?context=graph%2Fapi%2F1.0&view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from office365.teams.team import Team
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
# teams = client.teams.get_all().select(["displayName"]).execute_query()
teams = client.teams.get().paged().select(["displayName"]).execute_query()
for i, team in enumerate(teams):  # type: int, Team
    print("({0} of {1}) Name: {2}".format(i + 1, len(teams), team.display_name))
