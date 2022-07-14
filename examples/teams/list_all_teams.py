from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from office365.teams.team import Team

client = GraphClient(acquire_token_by_client_credentials)
teams = client.teams.get_all(include_properties=["displayName"]).execute_query()
for team in teams:  # type: Team
    print(team.display_name)
