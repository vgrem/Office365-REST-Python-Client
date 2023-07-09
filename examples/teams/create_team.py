"""
Create a new team.
`TeamCollection.create` is an async operation. To ensure teams gets created `Team.ensure_created` method is called

https://learn.microsoft.com/en-us/graph/api/team-post?view=graph-rest-1.0&tabs=http
"""

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
team_name = create_unique_name("Team")
print("Creating a team '{0}' ...".format(team_name))
new_team = client.teams.create(team_name).ensure_created().execute_query()
print("Team has been created")

print("Cleaning up temporary resources... ")
new_team.delete_object().execute_query()
