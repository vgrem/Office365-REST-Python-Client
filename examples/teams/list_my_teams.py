from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.teams.team import Team

client = GraphClient(acquire_token_by_username_password)
teams = client.me.joined_teams.get().execute_query()
for team in teams:  # type: Team
    print(team.display_name)
