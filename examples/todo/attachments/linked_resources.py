"""
Linked resources — connect a task to the item it came from.

A ``linkedResource`` points at the partner-app item associated with a task: the
Outlook email it was created from, a Teams message, or a deep link. This script
links one resource to a task, lists it, and removes it again.

    python linked_resources.py
    python linked_resources.py --task "Follow up" --keep

Requires delegated permission ``Tasks.ReadWrite`` for the signed-in user.

https://learn.microsoft.com/en-us/graph/api/resources/linkedresource
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


def _print_links(task) -> None:
    for resource in task.linked_resources.get().execute_query():
        print(f"  {resource.application_name:10s} {resource.display_name:30s} {resource.web_url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Link a partner-app item to a Microsoft To Do task")
    parser.add_argument("--task", default="Follow up with the vendor", help="task title")
    parser.add_argument("--keep", action="store_true", help="keep the list and task instead of deleting them")
    args = parser.parse_args()

    client = _client()
    try:
        task_list = client.me.todo.lists.ensure(LIST_NAME).execute_query()
        task = task_list.tasks.ensure(args.task).execute_query()

        for existing in task.linked_resources.get().execute_query():
            existing.delete_object().execute_query()

        task.linked_resources.add(
            applicationName="Outlook",
            displayName="Quote from the vendor",
            webUrl="https://outlook.office.com/mail/id/AAMkExample",
            externalId="AAMkExample",
        ).execute_query()

        print(f"Linked resources on {task.title!r}:")
        _print_links(task)

        for resource in task.linked_resources.get().execute_query():
            resource.delete_object().execute_query()
        remaining = list(task.linked_resources.get().execute_query())
        print(f"\nRemoved the link; {len(remaining)} resource(s) remain.")

        if args.keep:
            print("Keeping the list and task (--keep).")
            return
        task.delete_object().execute_query()
        client.me.todo.lists[task_list.id].delete_object().execute_query()
        print("Cleaned up the demo list and task.")
    except ClientRequestException as exc:
        if exc.code not in PERMISSION_CODES:
            raise
        print(f"To Do request failed: {exc.code}: {exc.message}")
        print("Grant and consent the delegated permission Tasks.ReadWrite for the signed-in user, then re-run.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
