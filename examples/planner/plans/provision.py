"""
Provision a whole plan from a template: categories, buckets, tasks, assignments.

The "sprint setup" pattern — create a plan, label its categories, add the board's
buckets, then create tasks with a priority, a category tag and an assignee. The
throwaway plan is deleted at the end — pass ``--keep`` to keep it.

    python provision.py
    python provision.py --keep

Requires delegated permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/planner-post-plans
https://learn.microsoft.com/en-us/graph/api/planner-post-buckets
https://learn.microsoft.com/en-us/graph/api/planner-post-tasks
"""

from __future__ import annotations

import argparse

from office365.directory.groups.group import Group
from office365.graph_client import GraphClient
from office365.planner.category_descriptions import PlannerCategoryDescriptions
from tests.settings import client_id, password, tenant, username

PLAN_PERMISSIONS = ("Group.ReadWrite.All",)
CATEGORIES = {"category1": "Critical", "category2": "Client", "category3": "Internal"}
BUCKETS = ["Backlog", "In Progress", "Review", "Done"]
TASKS = [
    {"title": "Kick-off meeting", "bucket": "Backlog", "category": "category3", "priority": 5},
    {"title": "Design review", "bucket": "In Progress", "category": "category2", "priority": 3},
    {"title": "API integration", "bucket": "Review", "category": "category1", "priority": 1},
]


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _resolve_group(client: GraphClient) -> Group | None:
    """The first unified (Microsoft 365) group — a plan needs a group owner."""
    groups = client.groups.filter("groupTypes/any(a:a eq 'unified')").top(1).get().execute_query()
    return groups[0] if len(groups) else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision a planner plan from a small template")
    parser.add_argument("--keep", action="store_true", help="keep the plan instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*PLAN_PERMISSIONS)
    group = _resolve_group(client)
    if group is None:
        print("No Microsoft 365 group found — a plan needs one. Create a group first.")
        return

    plan = client.planner.plans.add("SDK Planner tour — provisioned", group).execute_query()
    print(f"Plan: {plan.title!r}")
    try:
        details = plan.details.get().execute_query()
        details.category_descriptions = PlannerCategoryDescriptions(**CATEGORIES)
        details.update().execute_query()
        print("  categories:", ", ".join(CATEGORIES.values()))

        bucket_ids = {name: plan.buckets.add(name).execute_query().id for name in BUCKETS}
        print("  buckets:", ", ".join(BUCKETS))

        me = client.me.get().execute_query()
        for spec in TASKS:
            task = plan.tasks.add(spec["title"], bucket=bucket_ids[spec["bucket"]]).execute_query()
            task.priority = spec["priority"]
            task.set_property("appliedCategories", {spec["category"]: True})
            task.assign_to(me).update().execute_query()
            print(f"  task: {spec['title']}  (P{spec['priority']}, {CATEGORIES[spec['category']]})")
    finally:
        if not args.keep:
            plan.delete_object().execute_query()
            print("Deleted the plan (pass --keep to keep it).")


if __name__ == "__main__":
    main()
