"""
Task list lifecycle — create, inspect, rename, and delete To Do lists.

A task list is the top-level container in Microsoft To Do. This script lists the
existing lists (with their well-known kind and ownership flags), ensures a demo
list exists, renames it, and deletes it again — unless ``--keep`` is given, so
it is safe to re-run.

    python lifecycle.py
    python lifecycle.py --name Groceries --keep

Requires delegated permission ``Tasks.ReadWrite`` for the signed-in user.

https://learn.microsoft.com/en-us/graph/api/resources/todotasklist
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.todo.tasks.lists.list import TodoTaskList
from tests.settings import client_id, password, tenant, username

PERMISSION_CODES = {"accessDenied", "Authorization_RequestDenied", "ErrorAccessDenied", "Forbidden"}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _flags(task_list: TodoTaskList) -> str:
    flags = ["owned" if task_list.is_owner else "", "shared" if task_list.is_shared else ""]
    text = "/".join(flag for flag in flags if flag)
    return f"  [{text}]" if text else ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Microsoft To Do task list lifecycle")
    parser.add_argument("--name", default="SDK Lists Demo", help="name of the demo list")
    parser.add_argument("--keep", action="store_true", help="keep the demo list instead of deleting it")
    args = parser.parse_args()

    client = _client()
    try:
        lists = client.me.todo.lists.get().execute_query()
        print(f"Task lists before ({len(lists)}):")
        for task_list in lists:
            print(f"  {task_list.display_name:35s} kind={task_list.wellknown_list_name.name}{_flags(task_list)}")

        task_list = client.me.todo.lists.ensure(args.name).execute_query()
        print(f"\nEnsured list: {task_list.display_name} (id ends ...{task_list.id[-6:]})")

        task_list.set_property("displayName", f"{args.name} (renamed)")
        task_list.update().execute_query()
        print(f"Renamed to:   {task_list.display_name}")

        if args.keep:
            print("Keeping the demo list (--keep).")
            return

        task_list.delete_object().execute_query()
        print("Deleted the demo list.")
    except ClientRequestException as exc:
        if exc.code not in PERMISSION_CODES:
            raise
        print(f"To Do request failed: {exc.code}: {exc.message}")
        print("Grant and consent the delegated permission Tasks.ReadWrite for the signed-in user, then re-run.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
