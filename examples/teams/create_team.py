import json
import uuid

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient


def print_success(group):
    """
    :type group: office365.directory.groups.group.Group
    """
    print(f"team has been deleted")


client = GraphClient(acquire_token_by_username_password)
team_name = "Team_" + uuid.uuid4().hex
team = client.teams.create(team_name).execute_query()
print(json.dumps(team.to_json(), indent=4))

team.delete_object().execute_query_retry(success_callback=print_success)  # clean up
