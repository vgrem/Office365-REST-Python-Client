"""
List all teams in an organization (tenant)

https://learn.microsoft.com/en-us/graph/teams-list-all-teams?context=graph%2Fapi%2F1.0&view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
# teams = client.teams.get_all().select(["displayName"]).execute_query()  # get all at once
# teams = client.teams.get().paged().select(["displayName"]).execute_query()   # paged load
teams = client.teams.get().top(10).select(["displayName"]).execute_query()
for team in teams:
    print("Name: {0}".format(team))
