"""
Create a new team.

https://learn.microsoft.com/en-us/graph/api/team-post?view=graph-rest-1.0&tabs=http
"""
import json
import uuid
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password


def cleanup(team):
    """
    :type team: office365.teams.team.Team
    """
    def print_success(group):
        """
        :type group: office365.directory.groups.group.Group
        """
        print(f"team has been deleted")

    team.delete_object().execute_query_retry(success_callback=print_success)


client = GraphClient(acquire_token_by_username_password)
team_name = "Team_" + uuid.uuid4().hex
new_team = client.teams.create(team_name).execute_query()
print(json.dumps(new_team.to_json(), indent=4))

cleanup(new_team)
