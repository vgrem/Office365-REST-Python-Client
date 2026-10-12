"""
Planner in five minutes — list your plans, buckets and tasks.

Microsoft Planner is organized as a **plan** (owned by a Microsoft 365 group)
that contains **buckets** (the board's columns) and **tasks**. This script is
read-only: it walks the plans you can access and shows the buckets and tasks in
each.

    python quickstart.py
    python quickstart.py --plans 3 --tasks 20

Requires delegated permission ``Tasks.ReadWrite`` (or ``Group.Read.All``).

https://learn.microsoft.com/en-us/graph/api/planneruser-list-plans
https://learn.microsoft.com/en-us/graph/api/plannerplan-list-tasks
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

READ_PERMISSIONS = ("Tasks.ReadWrite", "Tasks.ReadWrite.All", "Group.Read.All", "Group.ReadWrite.All")


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def main() -> None:
    parser = argparse.ArgumentParser(description="List your planner plans, buckets and tasks")
    parser.add_argument("--plans", type=int, default=5, help="how many plans to show (default: 5)")
    parser.add_argument("--tasks", type=int, default=10, help="how many tasks per plan to show (default: 10)")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*READ_PERMISSIONS)

    plans = list(client.me.planner.plans.get().execute_query())
    if not plans:
        print("No plans found for the signed-in user.")
        return

    print(f"{len(plans)} plan(s) available; showing {min(args.plans, len(plans))}\n")
    for plan in plans[: args.plans]:
        buckets = list(plan.buckets.get().execute_query())
        tasks = list(plan.tasks.get().execute_query())
        bucket_names = {b.id: b.name for b in buckets}

        print(f"▸ {plan.title or '(untitled)'}")
        print(f"  buckets: {', '.join(b.name for b in buckets) or '—'}")
        print(f"  tasks:   {len(tasks)}")
        for task in tasks[: args.tasks]:
            where = bucket_names.get(task.bucket_id, "no bucket")
            print(f"    [{task.percent_complete:3d}%] {task.title}  ({where})")
        if len(tasks) > args.tasks:
            print(f"    … and {len(tasks) - args.tasks} more (raise --tasks)")
        print()


if __name__ == "__main__":
    main()
