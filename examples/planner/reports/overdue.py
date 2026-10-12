"""
Overdue and due-soon planner tasks.

Read-only: walks the plans you can access and reports the incomplete tasks that
are past their due date, optionally also the ones due within the next
``--days-ahead`` days, grouped by assignee. Graph returns the assignment map
keyed by user id; because it does not resolve display names there, the report
shows the id prefix.

    python overdue.py
    python overdue.py --days-ahead 7

Requires delegated permission ``Tasks.ReadWrite`` (or ``Group.Read.All``).

https://learn.microsoft.com/en-us/graph/api/planneruser-list-plans
https://learn.microsoft.com/en-us/graph/api/plannerplan-list-tasks
https://learn.microsoft.com/en-us/graph/api/resources/plannertask
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

READ_PERMISSIONS = ("Tasks.ReadWrite", "Tasks.ReadWrite.All", "Group.Read.All", "Group.ReadWrite.All")
COMPLETE = 100


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _due_date(task) -> datetime | None:
    due = task.due_date_time
    if due is None or due == datetime.min:
        return None
    return due


def main() -> None:
    parser = argparse.ArgumentParser(description="Report overdue and due-soon planner tasks")
    parser.add_argument("--plans", type=int, default=10, help="how many plans to scan (default: 10)")
    parser.add_argument("--days-ahead", type=int, default=0, help="also include tasks due within N days")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*READ_PERMISSIONS)

    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=args.days_ahead) if args.days_ahead > 0 else None
    rows: list[tuple[datetime, str, str, str, int]] = []

    for plan in list(client.me.planner.plans.get().execute_query())[: args.plans]:
        for task in plan.tasks.get().execute_query():
            due = _due_date(task)
            if due is None or (task.percent_complete or 0) >= COMPLETE:
                continue
            if due > now and (horizon is None or due > horizon):
                continue
            assignees = (
                ", ".join(user_id[:8] for user_id, value in task.assignments if value is not None) or "unassigned"
            )
            rows.append((due, task.title or "(untitled)", plan.title or "(untitled)", assignees, task.priority or 5))

    if not rows:
        scope = "" if horizon is None else f" or due within {args.days_ahead} day(s)"
        print(f"No overdue tasks found{scope}.")
        return

    rows.sort()
    scope = "" if horizon is None else f" or due within {args.days_ahead} day(s)"
    print(f"{len(rows)} task(s) overdue{scope}\n")
    print(f"{'due':<12} {'priority':<9} {'assignee':<10} task")
    for due, title, plan_title, assignees, priority in rows:
        flag = "overdue" if due <= now else "due soon"
        print(f"{due:%Y-%m-%d}   P{priority:<8} {assignees:<10} {title}  —  {plan_title}  [{flag}]")


if __name__ == "__main__":
    main()
