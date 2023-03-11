from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from office365.teams.team import Team

client = GraphClient(acquire_token_by_client_credentials)
teams = client.teams.get_all().select(["displayName"]).execute_query()
for i, team in enumerate(teams):  # type: int, Team
    print("({0} of {1}) Name: {2}".format(i + 1, len(teams), team.display_name))
