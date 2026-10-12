"""
The lifecycle of a planner task — create, update, complete, delete.

This script creates a throwaway plan with a bucket, creates a task in it, updates
the task's properties, marks it complete, deletes the task, then deletes the plan
— pass ``--keep`` to keep everything.

    python lifecycle.py
    python lifecycle.py --keep

Requires delegated permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/planner-post-tasks
https://learn.microsoft.com/en-us/graph/api/planner-update-tasks
https://learn.microsoft.com/en-us/graph/api/planner-delete-task
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.directory.groups.group import Group
from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

PLAN_PERMISSIONS = ("Group.ReadWrite.All",)
DUE_IN_DAYS = 7


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _resolve_group(client: GraphClient) -> Group | None:
    """The first unified (Microsoft 365) group — a plan needs a group owner."""
    groups = client.groups.filter("groupTypes/any(a:a eq 'unified')").top(1).get().execute_query()
    return groups[0] if len(groups) else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Create, update, complete and delete a planner task")
    parser.add_argument("--keep", action="store_true", help="keep the plan instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*PLAN_PERMISSIONS)
    group = _resolve_group(client)
    if group is None:
        print("No Microsoft 365 group found — a plan needs one. Create a group first.")
        return

    plan = client.planner.plans.add("SDK Planner tour — tasks", group).execute_query()
    try:
        bucket = plan.buckets.add("To do").execute_query()
        task = plan.tasks.add("Draft proposal", bucket=bucket).execute_query()
        print(f"Created task {task.title!r} in {bucket.name!r}")

        task.title = "Draft proposal v2"
        task.priority = 3
        task.due_date_time = datetime.now(timezone.utc) + timedelta(days=DUE_IN_DAYS)
        task.percent_complete = 50
        task.update().execute_query()
        print(f"Updated: {task.title!r}  P{task.priority}  {task.percent_complete}%  due {task.due_date_time:%Y-%m-%d}")

        task.percent_complete = 100
        task.update().execute_query()
        print(f"Completed: {task.percent_complete}%")

        task.delete_object().execute_query()
        print("Deleted the task")
    finally:
        if not args.keep:
            plan.delete_object().execute_query()
            print("Deleted the plan (pass --keep to keep it).")


if __name__ == "__main__":
    main()
