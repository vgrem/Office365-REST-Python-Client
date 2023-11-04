"""
Create a new plannerTask.
https://learn.microsoft.com/en-us/graph/api/planner-post-tasks?view=graph-rest-1.0
"""
import sys

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
group = client.groups.get_by_name("My Sample Team").get().execute_query()
plans = group.planner.plans.get().execute_query()
if len(plans) == 0:
    sys.exit("No plans were found")
task = plans[0].tasks.add(title="New task").execute_query()
print("Task {0} has been created".format(task.title))
