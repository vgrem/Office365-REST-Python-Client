"""
Delete completed tasks older than a specified number of days.

Pass --dry-run to only report what would be deleted.

Requires delegated permission Tasks.ReadWrite.

https://learn.microsoft.com/en-us/graph/api/todotask-delete
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.todo.tasks.taskstatus import TaskStatus
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Delete completed tasks older than N days")
    parser.add_argument("--days", type=int, default=30, help="delete tasks completed before this many days ago")
    parser.add_argument("--dry-run", action="store_true", help="report what would be deleted without deleting")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    deleted = 0
    for lst in client.me.todo.lists.get().execute_query():
        for task in lst.tasks.get().execute_query():
            if (
                task.status == TaskStatus.completed
                and task.last_modified_date_time
                and task.last_modified_date_time < cutoff
            ):
                print(f"  [{lst.display_name}]  {task.title or '?'}")
                deleted += 1
                if not args.dry_run:
                    task.delete_object().execute_query()

    verb = "Would delete" if args.dry_run else "Deleted"
    print(f"{verb} {deleted} completed tasks older than {args.days} days")


if __name__ == "__main__":
    main()
