from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_client_credentials)
teams = client.teams.get_all(["displayName"]).execute_query()
for team in teams:
    print(team.displayName)
