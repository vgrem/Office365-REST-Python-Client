"""
Create a new team.


Since `TeamCollection.create` is an async operation, execute_query_and_wait is called to ensure teams gets created

https://learn.microsoft.com/en-us/graph/api/team-post?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    create_unique_name,
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
team_name = create_unique_name("Team")
print("Creating a team '{0}' ...".format(team_name))
team = client.teams.create(team_name).execute_query_and_wait()
print("Team has been created")

print("Cleaning up temporary resources... ")
team.delete_object().execute_query()
