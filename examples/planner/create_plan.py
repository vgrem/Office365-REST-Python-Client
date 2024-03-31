"""
Creates a new planner plan
https://learn.microsoft.com/en-us/graph/api/planner-post-plans?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
group = client.groups.get_by_name("My Sample Team")
plan = client.planner.plans.add("My Plan", group).execute_query()
print(plan)


plan.delete_object().execute_query()  # clean up
