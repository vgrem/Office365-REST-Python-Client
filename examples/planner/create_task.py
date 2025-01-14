"""
Create a new plannerTask.
https://learn.microsoft.com/en-us/graph/api/planner-post-tasks?view=graph-rest-1.0
"""

import sys

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
group = client.groups.get_by_name("My Sample Team").get().execute_query()
plans = group.planner.plans.get().execute_query()
if len(plans) == 0:
    sys.exit("No plans were found")
task = plans[0].tasks.add(title="New task").execute_query()
print("Task {0} has been created".format(task.title))
