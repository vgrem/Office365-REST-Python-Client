"""
Read and label a plan's categories.

Each plan has a **details** object that stores up to 25 category labels
(``category1`` … ``category25``) — the color tags shown on tasks. This script
creates a throwaway plan, labels three categories, reads them back, then deletes
the plan — pass ``--keep`` to keep it.

    python details.py
    python details.py --keep

Requires delegated permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/planner-get-plandetails
https://learn.microsoft.com/en-us/graph/api/planner-update-plandetails
"""

from __future__ import annotations

import argparse

from office365.directory.groups.group import Group
from office365.graph_client import GraphClient
from office365.planner.category_descriptions import PlannerCategoryDescriptions
from tests.settings import client_id, password, tenant, username

PLAN_PERMISSIONS = ("Group.ReadWrite.All",)
CATEGORIES = {"category1": "Urgent", "category2": "Client work", "category3": "Internal"}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _resolve_group(client: GraphClient) -> Group | None:
    """The first unified (Microsoft 365) group — a plan needs a group owner."""
    groups = client.groups.filter("groupTypes/any(a:a eq 'unified')").top(1).get().execute_query()
    return groups[0] if len(groups) else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Label a planner plan's categories")
    parser.add_argument("--keep", action="store_true", help="keep the plan instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*PLAN_PERMISSIONS)
    group = _resolve_group(client)
    if group is None:
        print("No Microsoft 365 group found — a plan needs one. Create a group first.")
        return

    plan = client.planner.plans.add("SDK Planner tour — details", group).execute_query()
    try:
        details = plan.details.get().execute_query()
        details.category_descriptions = PlannerCategoryDescriptions(**CATEGORIES)
        details.update().execute_query()
        print("Set categories:", ", ".join(f"{key[8:]} → {value}" for key, value in CATEGORIES.items()))

        labels = plan.details.get().execute_query().category_descriptions
        read_back = f"category1={labels.category1!r}, category2={labels.category2!r}, category3={labels.category3!r}"
        print("Read back:", read_back)
    finally:
        if not args.keep:
            plan.delete_object().execute_query()
            print("Deleted the plan (pass --keep to keep it).")


if __name__ == "__main__":
    main()
