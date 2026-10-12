"""
A progress dashboard for the plans you can access.

Read-only: walks ``me/planner/plans`` and their tasks and prints the tasks by
percent complete and priority, with a small bar chart. Because Graph ignores
``$filter``/``$orderby`` on a plan's tasks, the aggregation happens in Python.

    python progress_report.py
    python progress_report.py --plans 3

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


def _bar(count: int) -> str:
    return "█" * count


def main() -> None:
    parser = argparse.ArgumentParser(description="Progress dashboard across your planner plans")
    parser.add_argument("--plans", type=int, default=10, help="how many plans to scan (default: 10)")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*READ_PERMISSIONS)

    plans = list(client.me.planner.plans.get().execute_query())[: args.plans]
    if not plans:
        print("No plans found for the signed-in user.")
        return

    by_progress: dict[int, int] = {}
    by_priority: dict[int, int] = {}
    total = 0
    for plan in plans:
        tasks = list(plan.tasks.get().execute_query())
        total += len(tasks)
        print(f"▸ {plan.title or '(untitled)'}  ({len(tasks)} task(s))")
        for task in tasks:
            percent = task.percent_complete or 0
            priority = task.priority or 5
            by_progress[percent] = by_progress.get(percent, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
            assignees = (
                ", ".join(user_id[:8] for user_id, value in task.assignments if value is not None) or "unassigned"
            )
            print(f"    [{percent:3d}%] P{priority:<2d} {task.title}  ({assignees})")
        print()

    print(f"Total: {total} task(s) across {len(plans)} plan(s)\n")
    print("By percent complete:")
    for percent in sorted(by_progress):
        print(f"  {percent:3d}%: {by_progress[percent]:3d}  {_bar(by_progress[percent])}")
    print("\nBy priority:")
    for priority in sorted(by_priority):
        print(f"  P{priority}: {by_priority[priority]:3d}  {_bar(by_priority[priority])}")


if __name__ == "__main__":
    main()
