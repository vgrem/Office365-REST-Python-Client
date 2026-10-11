"""
Cleanup — remove old completed tasks.

Completed tasks pile up in To Do and are rarely revisited. This maintenance
script scans every list, finds tasks that were completed more than a given
number of days ago, and deletes them. It is a **dry run by default**: pass
``--apply`` to actually delete.

    python cleanup.py
    python cleanup.py --days 14 --list Groceries --apply

Requires delegated permission ``Tasks.ReadWrite`` for the signed-in user.

https://learn.microsoft.com/en-us/graph/api/todotask-delete
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.todo.tasks.task import TodoTask
from tests.settings import client_id, password, tenant, username

PERMISSION_CODES = {"accessDenied", "Authorization_RequestDenied", "ErrorAccessDenied", "Forbidden"}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _completed_at(task: TodoTask) -> datetime | None:
    value = task.completed_date_time.dateTime
    if value:
        try:
            return datetime.fromisoformat(value.split(".")[0]).replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    moment = task.last_modified_date_time
    if not moment or moment == datetime.min:
        return None
    return moment.replace(tzinfo=timezone.utc) if moment.tzinfo is None else moment


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete old completed Microsoft To Do tasks")
    parser.add_argument("--days", type=int, default=30, help="age in days of completed tasks to remove (default: 30)")
    parser.add_argument("--list", help="only this task list (default: every list)")
    parser.add_argument("--apply", action="store_true", help="actually delete (default: dry run)")
    args = parser.parse_args()

    client = _client()
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    deleted = 0
    try:
        lists = client.me.todo.lists.get().execute_query()
        if args.list:
            lists = [task_list for task_list in lists if task_list.display_name == args.list]
            if not lists:
                print(f"No task list named {args.list!r}.")
                return

        mode = "Deleting" if args.apply else "Would delete"
        for task_list in lists:
            stale = [
                (task, completed)
                for task in task_list.tasks.filter("status eq 'completed'").get().execute_query()
                if (completed := _completed_at(task)) is not None and completed < cutoff
            ]
            for task, completed in stale:
                print(f"  {mode}: {task.title!r} (completed {completed:%Y-%m-%d}) in {task_list.display_name!r}")
                if args.apply:
                    task.delete_object().execute_query()
            deleted += len(stale)

        verb = "Deleted" if args.apply else "Found"
        print(f"\n{verb} {deleted} completed task(s) older than {args.days} days.")
        if not args.apply:
            print("Dry run — pass --apply to delete them.")
    except ClientRequestException as exc:
        if exc.code not in PERMISSION_CODES:
            raise
        print(f"To Do request failed: {exc.code}: {exc.message}")
        print("Grant and consent the delegated permission Tasks.ReadWrite for the signed-in user, then re-run.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
