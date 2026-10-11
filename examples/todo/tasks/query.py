"""
Find tasks due within a specified number of days.

Requires delegated permission Tasks.Read.

https://learn.microsoft.com/en-us/graph/api/todotask-list
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Show tasks due within the next N days")
    parser.add_argument("--days", type=int, default=7, help="look ahead this many days (default 7)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    cutoff = datetime.now(timezone.utc) + timedelta(days=args.days)
    cutoff_utc = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

    for lst in client.me.todo.lists.get().execute_query():
        for task in lst.tasks.filter(f"dueDateTime/dateTime le '{cutoff_utc}'").get().execute_query():
            print(f"  [{lst.display_name}]  {task.title:50s}  due={task.due_date_time}")


if __name__ == "__main__":
    main()
