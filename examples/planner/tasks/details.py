"""
Work with a task's details — the description and the checklist.

Each task has a **details** object holding the free-text description and the
checklist. Checklist items are keyed by a client-generated id; because PATCH
merges the map, removal means sending ``null`` for the id — ``set_checklist``
does that for you when you want to replace the whole list. This script creates a
throwaway task, edits its details, then deletes the plan (pass ``--keep``).

    python details.py
    python details.py --keep

Requires delegated permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/planner-get-taskdetails
https://learn.microsoft.com/en-us/graph/api/planner-update-taskdetails
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


def _print_checklist(details) -> None:
    for _, item in details.checklist:
        print(f"  [{'x' if item.isChecked else ' '}] {item.title}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Edit a planner task's description and checklist")
    parser.add_argument("--keep", action="store_true", help="keep the plan instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*PLAN_PERMISSIONS)
    group = _resolve_group(client)
    if group is None:
        print("No Microsoft 365 group found — a plan needs one. Create a group first.")
        return

    plan = client.planner.plans.add("SDK Planner tour — details", group).execute_query()
    try:
        task = plan.tasks.add("Write the spec").execute_query()

        details = task.details.get().execute_query()
        details.description = "Cover scope, milestones and risks."
        details.preview_type = "description"
        details.add_checklist_item("Outline", is_checked=True).add_checklist_item("Draft")
        details.update().execute_query()
        print(f"Description: {details.description!r}")
        print("Checklist:")
        _print_checklist(details)

        details = task.details.get().execute_query()
        details.set_checklist(["Outline", "Draft", "Review"])
        details.update().execute_query()
        print("After set_checklist(['Outline', 'Draft', 'Review']):")
        _print_checklist(task.details.get().execute_query())
    finally:
        if not args.keep:
            plan.delete_object().execute_query()
            print("Deleted the plan (pass --keep to keep it).")


if __name__ == "__main__":
    main()
