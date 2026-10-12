"""
Assign and unassign a task.

The task's ``assignments`` map is keyed by user id. This script creates a
throwaway plan and task, assigns the signed-in user, shows the assignment, then
unassigns — and deletes the plan (pass ``--keep`` to keep it).

    python assignments.py
    python assignments.py --keep

Requires delegated permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/planner-update-tasks
"""

from __future__ import annotations

import argparse

from office365.directory.groups.group import Group
from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

PLAN_PERMISSIONS = ("Group.ReadWrite.All",)


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _resolve_group(client: GraphClient) -> Group | None:
    """The first unified (Microsoft 365) group — a plan needs a group owner."""
    groups = client.groups.filter("groupTypes/any(a:a eq 'unified')").top(1).get().execute_query()
    return groups[0] if len(groups) else None


def _assignee_ids(task) -> list[str]:
    return [user_id for user_id, value in task.assignments if value is not None]


def main() -> None:
    parser = argparse.ArgumentParser(description="Assign and unassign a planner task")
    parser.add_argument("--keep", action="store_true", help="keep the plan instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*PLAN_PERMISSIONS)
    group = _resolve_group(client)
    if group is None:
        print("No Microsoft 365 group found — a plan needs one. Create a group first.")
        return

    plan = client.planner.plans.add("SDK Planner tour — assignments", group).execute_query()
    try:
        task = plan.tasks.add("Review the design").execute_query()
        me = client.me.get().execute_query()

        task.assign_to(me).update().execute_query()
        print(f"Assigned to {me.user_principal_name}:", _assignee_ids(task) or "nobody")

        task.unassign(me).update().execute_query()
        print("After unassign:", _assignee_ids(task) or "nobody")
    finally:
        if not args.keep:
            plan.delete_object().execute_query()
            print("Deleted the plan (pass --keep to keep it).")


if __name__ == "__main__":
    main()
