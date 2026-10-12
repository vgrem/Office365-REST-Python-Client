"""
The lifecycle of a board bucket — add, rename, look up, delete.

A bucket is a column of the plan's board. This script creates a throwaway plan,
adds a few buckets, renames one, looks it up by name, deletes it, then deletes
the plan — pass ``--keep`` to keep everything.

    python lifecycle.py
    python lifecycle.py --keep

Requires delegated permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/planner-post-buckets
https://learn.microsoft.com/en-us/graph/api/planner-list-buckets
https://learn.microsoft.com/en-us/graph/api/planner-update-bucket
https://learn.microsoft.com/en-us/graph/api/planner-delete-bucket
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
    parser = argparse.ArgumentParser(description="Add, rename, look up and delete board buckets")
    parser.add_argument("--keep", action="store_true", help="keep the plan instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*PLAN_PERMISSIONS)
    group = _resolve_group(client)
    if group is None:
        print("No Microsoft 365 group found — a plan needs one. Create a group first.")
        return

    plan = client.planner.plans.add("SDK Planner tour — buckets", group).execute_query()
    try:
        backlog = plan.buckets.add("Backlog").execute_query()
        plan.buckets.add("In Progress").execute_query()
        plan.buckets.add("Done").execute_query()
        print("Buckets:", ", ".join(b.name for b in plan.buckets.get().execute_query()))

        backlog.name = "Backlog (renamed)"
        backlog.update().execute_query()
        print(f"Renamed a bucket to {backlog.name!r}")

        found = plan.buckets.find_by_name("Backlog (renamed)").execute_query()
        print(f"find_by_name -> {found.name!r} (loaded={found.is_loaded})")

        found.delete_object().execute_query()
        print("After delete:", ", ".join(b.name for b in plan.buckets.get().execute_query()))
    finally:
        if not args.keep:
            plan.delete_object().execute_query()
            print("Deleted the plan (pass --keep to keep it).")


if __name__ == "__main__":
    main()
