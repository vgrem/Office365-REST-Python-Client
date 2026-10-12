"""
Query a plan's tasks.

``$select`` is honoured on a plan's tasks, but ``$filter``, ``$orderby`` and
``$top`` are ignored by Graph — only ``$filter=planId eq '…'`` works on the
top-level task set. This script creates a few tasks and shows both styles: narrow
the payload with ``$select``, then filter and sort in Python, and look a task up
by title with ``find_by_title``.

    python query.py
    python query.py --keep

Requires delegated permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/plannerplan-list-tasks
https://learn.microsoft.com/en-us/graph/api/plannertask-get
"""

from __future__ import annotations

import argparse

from office365.directory.groups.group import Group
from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

PLAN_PERMISSIONS = ("Group.ReadWrite.All",)
COMPLETE = 100
SEED = [("Triage inbox", 0, 5), ("Draft proposal", 50, 3), ("Ship release", COMPLETE, 1)]


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _resolve_group(client: GraphClient) -> Group | None:
    """The first unified (Microsoft 365) group — a plan needs a group owner."""
    groups = client.groups.filter("groupTypes/any(a:a eq 'unified')").top(1).get().execute_query()
    return groups[0] if len(groups) else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Query a planner plan's tasks")
    parser.add_argument("--keep", action="store_true", help="keep the plan instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*PLAN_PERMISSIONS)
    group = _resolve_group(client)
    if group is None:
        print("No Microsoft 365 group found — a plan needs one. Create a group first.")
        return

    plan = client.planner.plans.add("SDK Planner tour — query", group).execute_query()
    try:
        for title, percent, priority in SEED:
            task = plan.tasks.add(title).execute_query()
            task.percent_complete = percent
            task.priority = priority
            task.update().execute_query()

        # $select narrows the payload to just the fields we need ...
        rows = plan.tasks.select(["id", "title", "percentComplete", "priority"]).get().execute_query()
        # ... but $filter/$orderby/$top are ignored, so filter and sort here.
        open_tasks = sorted((t for t in rows if t.percent_complete < COMPLETE), key=lambda t: t.priority)
        print("Open tasks by priority:")
        for task in open_tasks:
            print(f"  P{task.priority}  {task.percent_complete:3d}%  {task.title}")

        found = plan.tasks.find_by_title("Draft proposal").execute_query()
        print(f"find_by_title('Draft proposal') -> {found.title!r} (loaded={found.is_loaded})")
    finally:
        if not args.keep:
            plan.delete_object().execute_query()
            print("Deleted the plan (pass --keep to keep it).")


if __name__ == "__main__":
    main()
