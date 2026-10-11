"""
Task search — filter tasks by status, importance, and due date.

Builds an OData ``$filter`` from the command line and prints the matches, sorted
client-side. Without ``--list`` it scans every task list. Use it for the "what is
overdue?" and "what is due this week?" questions.

    python query.py
    python query.py --overdue
    python query.py --due-within 7 --importance high
    python query.py --status completed --limit 50

A bound such as ``dueDateTime/dateTime lt '…'`` also matches tasks that have no
``dueDateTime`` (Graph treats null as smaller than any value), and
``dueDateTime ne null`` is not supported, so the script always adds a lower
bound to exclude tasks without a due date.

Requires delegated permission ``Tasks.ReadWrite`` (``Tasks.Read`` is enough for
read-only access).

https://learn.microsoft.com/en-us/graph/api/todotasklist-list-tasks
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.outlook.mail.importance import Importance
from office365.runtime.client_request_exception import ClientRequestException
from office365.todo.tasks.task import TodoTask
from tests.settings import client_id, password, tenant, username

PERMISSION_CODES = {"accessDenied", "Authorization_RequestDenied", "ErrorAccessDenied", "Forbidden"}
_IMPORTANCE_ORDER = {Importance.high: 0, Importance.normal: 1, Importance.low: 2}
_EPOCH = datetime.min.replace(tzinfo=timezone.utc)
# A task with no due date also matches `dueDateTime/dateTime lt …` (Graph treats null
# as smaller than any value), so bound the range to exclude "no due date" tasks.
_MIN_DUE = "1900-01-01T00:00:00.0000000Z"


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.split(".")[0]).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _filter_clause(args: argparse.Namespace, now: datetime) -> str:
    clauses: list[str] = []
    if args.overdue or args.status == "open":
        clauses.append("status ne 'completed'")
    elif args.status == "completed":
        clauses.append("status eq 'completed'")
    if args.importance:
        clauses.append(f"importance eq '{args.importance}'")
    stamp = now.strftime("%Y-%m-%dT%H:%M:%S.0000000Z")
    if args.overdue:
        clauses.append(f"dueDateTime/dateTime gt '{_MIN_DUE}'")
        clauses.append(f"dueDateTime/dateTime lt '{stamp}'")
    elif args.due_within is not None:
        cutoff = now + timedelta(days=args.due_within)
        clauses.append(f"dueDateTime/dateTime gt '{stamp}'")
        clauses.append(f"dueDateTime/dateTime lt '{cutoff.strftime('%Y-%m-%dT%H:%M:%S.0000000Z')}'")
    return " and ".join(clauses)


def _sort_key(order_by: str):
    if order_by == "importance":
        return lambda task: (
            _IMPORTANCE_ORDER.get(task.importance, 9),
            _parse(task.due_date_time.dateTime) or _EPOCH,
        )
    if order_by == "title":
        return lambda task: (task.title or "").lower()
    return lambda task: (_parse(task.due_date_time.dateTime) or datetime.max.replace(tzinfo=timezone.utc),)


def _print_task(task: TodoTask, list_name: str) -> None:
    due = task.due_date_time.dateTime or "-"
    status = task.status.name if task.status else "-"
    importance = task.importance.name if task.importance else "-"
    print(f"  {task.title:40s} [{list_name}] due={due[:16]} {status:8s} {importance}")
    for item in task.checklist_items.get().execute_query():
        mark = "x" if item.is_checked else " "
        print(f"      [{mark}] {item.display_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Microsoft To Do tasks")
    parser.add_argument("--list", help="only this task list (default: every list)")
    parser.add_argument("--status", choices=["open", "completed", "all"], default="open")
    parser.add_argument("--importance", choices=[item.name for item in Importance], help="filter by importance")
    parser.add_argument("--due-within", type=int, metavar="DAYS", help="due within the next DAYS days")
    parser.add_argument("--overdue", action="store_true", help="only overdue (incomplete) tasks")
    parser.add_argument("--order-by", choices=["due", "importance", "title"], default="due")
    parser.add_argument("--limit", type=int, default=20, help="maximum tasks to print per list (default: 20)")
    args = parser.parse_args()

    client = _client()
    now = datetime.now(timezone.utc)
    clause = _filter_clause(args, now)
    shown = 0
    try:
        lists = client.me.todo.lists.get().execute_query()
        if args.list:
            lists = [task_list for task_list in lists if task_list.display_name == args.list]
            if not lists:
                print(f"No task list named {args.list!r}.")
                return
        for task_list in lists:
            tasks = list(task_list.tasks.filter(clause).get().execute_query())
            tasks.sort(key=_sort_key(args.order_by))
            for task in tasks[: args.limit]:
                _print_task(task, task_list.display_name)
            shown += min(len(tasks), args.limit)
        print(f"\nMatched {shown} task(s)  [filter: {clause or 'none'}]")
    except ClientRequestException as exc:
        if exc.code not in PERMISSION_CODES:
            raise
        print(f"To Do request failed: {exc.code}: {exc.message}")
        print("Grant and consent the delegated permission Tasks.ReadWrite for the signed-in user, then re-run.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
