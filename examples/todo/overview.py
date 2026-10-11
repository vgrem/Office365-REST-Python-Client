"""
To Do overview — a read-only dashboard across every task list.

Walks all of the signed-in user's lists and reports, per list, how many tasks
are open, completed, or overdue, plus a grand total. It is the fastest read-only
way to see what is on the plate and the shape of a To Do account.

    python overview.py

Requires delegated permission ``Tasks.ReadWrite`` (``Tasks.Read`` is enough for
read-only access).

https://learn.microsoft.com/en-us/graph/api/resources/todotask
"""

from __future__ import annotations

from datetime import datetime, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.todo.tasks.taskstatus import TaskStatus
from tests.settings import client_id, password, tenant, username

PERMISSION_CODES = {"accessDenied", "Authorization_RequestDenied", "ErrorAccessDenied", "Forbidden"}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _parse(value: str | None) -> datetime | None:
    """Parse a Graph date-time string, ignoring the fractional seconds."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.split(".")[0]).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _is_overdue(task, now: datetime) -> bool:
    due = _parse(task.due_date_time.dateTime)
    return task.status != TaskStatus.completed and due is not None and due < now


def main() -> None:
    client = _client()
    now = datetime.now(timezone.utc)
    totals = {"tasks": 0, "open": 0, "completed": 0, "overdue": 0}

    try:
        print(f"{'Task list':38s} {'open':>5s} {'done':>5s} {'late':>5s} {'total':>6s}")
        print("-" * 64)
        for task_list in client.me.todo.lists.get().execute_query():
            tasks = list(task_list.tasks.get().execute_query())
            open_count = sum(1 for task in tasks if task.status != TaskStatus.completed)
            completed = len(tasks) - open_count
            overdue = sum(1 for task in tasks if _is_overdue(task, now))
            totals["tasks"] += len(tasks)
            totals["open"] += open_count
            totals["completed"] += completed
            totals["overdue"] += overdue
            print(f"{task_list.display_name:38s} {open_count:5d} {completed:5d} {overdue:5d} {len(tasks):6d}")
        print("-" * 64)
        print(f"{'TOTAL':38s} {totals['open']:5d} {totals['completed']:5d} {totals['overdue']:5d} {totals['tasks']:6d}")
    except ClientRequestException as exc:
        if exc.code not in PERMISSION_CODES:
            raise
        print(f"To Do request failed: {exc.code}: {exc.message}")
        print("Grant and consent the delegated permission Tasks.ReadWrite for the signed-in user, then re-run.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
