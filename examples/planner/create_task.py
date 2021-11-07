from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.planner.plans.plan import PlannerPlan


def ensure_plan(planner, name):
    """
    :type planner: office365.planner.planner_user.PlannerUser
    :type name: str
    :rtype: PlannerPlan
    """
    plans = planner.plans.get().filter("title eq '{0}'".format(name)).execute_query()
    if len(plans) > 0:
        return plans[0]
    else:
        return planner.plans.add(title=name).execute_query()


client = GraphClient(acquire_token_by_username_password)
plan = ensure_plan(client.me.planner, "My plan")
task = client.planner.tasks.add(title="New task", planId=plan.id).execute_query()
print("Task {0} has been created".format(task.title))
