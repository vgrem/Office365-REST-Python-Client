"""
Microsoft To Do quickstart — create a list, add a task, tick it off.

The shortest end-to-end path through the To Do API: reuse (or create) a list,
add a task that is due soon, break it into checklist subtasks, mark it complete,
then clean everything up. Re-runnable — the list is reused by name and the task
is removed at the end.

    python quickstart.py
    python quickstart.py --keep

Requires delegated permission ``Tasks.ReadWrite`` for the signed-in user.

https://learn.microsoft.com/en-us/graph/api/resources/todo-overview
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.mail.importance import Importance
from office365.runtime.client_request_exception import ClientRequestException
from office365.todo.tasks.taskstatus import TaskStatus
from tests.settings import client_id, password, tenant, username

LIST_NAME = "SDK Quickstart"
TASK_TITLE = "Prepare the quarterly report"
PERMISSION_CODES = {"accessDenied", "Authorization_RequestDenied", "ErrorAccessDenied", "Forbidden"}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _checklist_items(task) -> list[str]:
    return [item.display_name for item in task.checklist_items.get().execute_query()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Microsoft To Do end-to-end quickstart")
    parser.add_argument("--keep", action="store_true", help="keep the list and task instead of deleting them")
    args = parser.parse_args()

    client = _client()
    try:
        task_list = client.me.todo.lists.ensure(LIST_NAME).execute_query()
        print(f"List ready: {task_list.display_name}")

        due = datetime.now(timezone.utc) + timedelta(days=2)
        task = task_list.tasks.add(
            TASK_TITLE,
            due_date_time=due,
            importance=Importance.high,
            body="Collect the numbers, review with finance, publish.",
        ).execute_query()
        print(f"Task created: {task.title} (due {task.due_date_time}, {task.importance.name})")

        for title in ("Collect the numbers", "Review with finance", "Publish"):
            task.checklist_items.add(displayName=title).execute_query()
        print(f"Checklist: {', '.join(_checklist_items(task))}")

        task.status = TaskStatus.completed
        task.set_property("completedDateTime", DateTimeTimeZone.parse(datetime.now(timezone.utc)))
        task.update().execute_query()
        print(f"Task completed: {task.title} -> {task.status.name}")

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
