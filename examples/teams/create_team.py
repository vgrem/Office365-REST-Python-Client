"""
Create a new team.


Since `TeamCollection.create` is an async operation, execute_query_and_wait is called to ensure teams gets created

https://learn.microsoft.com/en-us/graph/api/team-post?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
team_name = create_unique_name("Team")
print("Creating a team '{0}' ...".format(team_name))
team = client.teams.create(team_name).execute_query_and_wait()
print("Team has been created")

print("Cleaning up temporary resources... ")
team.delete_object().execute_query()
