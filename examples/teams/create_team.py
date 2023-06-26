"""
Create a new team (async operation)

https://learn.microsoft.com/en-us/graph/api/team-post?view=graph-rest-1.0&tabs=http
"""
import uuid

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
team_name = "Team_" + uuid.uuid4().hex
new_team = client.teams.create(team_name).ensure_created().execute_query()
new_team.delete_object().execute_query()
