import uuid

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient


def print_failure(retry_number):
    print(f"{retry_number}: trying to create a team...")


client = GraphClient(acquire_token_by_client_credentials)
group_name = "Team_" + uuid.uuid4().hex
result = client.teams.create(group_name).execute_query_retry(max_retry=5, failure_callback=print_failure)
print("Team has been provisioned")
