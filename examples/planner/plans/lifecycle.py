"""
The lifecycle of a planner plan — create, rename, delete.

A plan is owned by a Microsoft 365 group. This script creates a throwaway plan in
the first unified group it finds, renames it, then deletes it again so the tenant
is left as it was — pass ``--keep`` to keep the plan.

    python lifecycle.py
    python lifecycle.py --keep

Requires delegated permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/planner-post-plans
https://learn.microsoft.com/en-us/graph/api/planner-update-plan
https://learn.microsoft.com/en-us/graph/api/planner-delete-plan
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Create, rename and delete a planner plan")
    parser.add_argument("--keep", action="store_true", help="keep the plan instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*PLAN_PERMISSIONS)
    group = _resolve_group(client)
    if group is None:
        print("No Microsoft 365 group found — a plan needs one. Create a group first.")
        return

    plan = client.planner.plans.add("SDK Planner tour", group).execute_query()
    print(f"Created plan {plan.title!r}  (id {plan.id})")

    plan.title = "SDK Planner tour (renamed)"
    plan.update().execute_query()
    print(f"Renamed to {plan.title!r}")

    if not args.keep:
        plan.delete_object().execute_query()
        print("Deleted the plan again (pass --keep to keep it).")


if __name__ == "__main__":
    main()
