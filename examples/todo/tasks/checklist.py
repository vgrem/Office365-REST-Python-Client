"""
Checklist subtasks — break a task into smaller, checkable steps.

A ``checklistItem`` is a lightweight subtask: it has a ``displayName`` and an
``isChecked`` flag, but no owner or due date. This script adds a checklist to a
task, ticks one item, renames another, removes a third, and prints the result.
Cleans up unless ``--keep`` is given.

    python checklist.py
    python checklist.py --task "Plan the sprint" --keep

Requires delegated permission ``Tasks.ReadWrite`` for the signed-in user.

https://learn.microsoft.com/en-us/graph/api/resources/checklistitem
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username

LIST_NAME = "SDK Tasks Demo"
PERMISSION_CODES = {"accessDenied", "Authorization_RequestDenied", "ErrorAccessDenied", "Forbidden"}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _print_checklist(task) -> None:
    for item in task.checklist_items.get().execute_query():
        print(f"  [{'x' if item.is_checked else ' '}] {item.display_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Microsoft To Do checklist subtasks")
    parser.add_argument("--task", default="Plan the sprint", help="task title")
    parser.add_argument("--keep", action="store_true", help="keep the list and task instead of deleting them")
    args = parser.parse_args()

    client = _client()
    try:
        task_list = client.me.todo.lists.ensure(LIST_NAME).execute_query()
        task = task_list.tasks.find_by_title(args.task).execute_query()
        if not task.is_loaded:
            task = task_list.tasks.add(args.task).execute_query()

        for item in task.checklist_items.get().execute_query():
            item.delete_object().execute_query()

        items = [task.checklist_items.add(displayName=title).execute_query() for title in ("Draft", "Review", "Ship")]
        print(f"Checklist for {task.title!r}:")
        _print_checklist(task)

        items[0].set_property("isChecked", True)
        items[0].update().execute_query()
        items[1].set_property("displayName", "Review with the team")
        items[1].update().execute_query()
        items[2].delete_object().execute_query()

        print("\nAfter checking, renaming, and deleting:")
        _print_checklist(task)

        if args.keep:
            print("\nKeeping the list and task (--keep).")
            return
        task.delete_object().execute_query()
        client.me.todo.lists[task_list.id].delete_object().execute_query()
        print("\nCleaned up the demo list and task.")
    except ClientRequestException as exc:
        if exc.code not in PERMISSION_CODES:
            raise
        print(f"To Do request failed: {exc.code}: {exc.message}")
        print("Grant and consent the delegated permission Tasks.ReadWrite for the signed-in user, then re-run.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
