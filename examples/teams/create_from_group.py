"""
Create team from group

https://learn.microsoft.com/en-us/graph/api/team-put-teams?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    create_unique_name,
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)


def print_failure(retry_number, ex):
    print(f"{retry_number}: Team creation still in progress, waiting...")


client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
group_name = create_unique_name("Flight")
group = client.groups.create_m365(group_name)
team = group.add_team().execute_query_retry(
    max_retry=10, failure_callback=print_failure
)
print("Team has been created:  {0}".format(team.web_url))

# clean up resources
print("Deleting a group...")
group.delete_object(True).execute_query()
