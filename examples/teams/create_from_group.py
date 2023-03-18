import uuid

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient


def print_failure(retry_number, ex):
    print(f"{retry_number}: re-trying to create a team...")


client = GraphClient(acquire_token_by_username_password)
group_name = "Team_" + uuid.uuid4().hex
group = client.groups.create_with_team(group_name).execute_query_retry(max_retry=5, failure_callback=print_failure)

#clean up
group.delete_object(True).execute_query()
