"""
List all task lists with their task counts.

Optionally filter by task list name.

Requires delegated permission Tasks.Read.

https://learn.microsoft.com/en-us/graph/api/todotasklist-list
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="List task lists with task counts")
    parser.add_argument("--name", default=None, help="only show the task list with this name")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    lists = client.me.todo.lists.get().execute_query()
    for lst in lists:
        if args.name and lst.display_name != args.name:
            continue
        tasks = lst.tasks.get().execute_query()
        print(f"  {lst.display_name:40s}  ({len(tasks)} tasks)")


if __name__ == "__main__":
    main()
