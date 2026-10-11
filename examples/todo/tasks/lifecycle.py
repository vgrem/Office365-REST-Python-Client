"""
Microsoft To-Do — manage task lists, tasks, and checklist items.

Covers the task lifecycle with subcommands:

  lists                  List task lists with task counts
  tasks                  Show tasks in a list
  add-list               Create a task list
  add-task               Create a task
  checklist              List (or add) checklist items on a task
  complete               Mark a task as completed
  delete-list            Delete a task list

Requires delegated permission ``Tasks.ReadWrite``. The To Do API operates on
the signed-in user's mailbox, so delegated auth is required.

https://learn.microsoft.com/en-us/graph/api/resources/todotask
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.outlook.mail.importance import Importance
from office365.todo.tasks.lists.list import TodoTaskList
from office365.todo.tasks.task import TodoTask
from office365.todo.tasks.taskstatus import TaskStatus
from tests.settings import client_id, password, tenant, username

IMPORTANCE = {"low": Importance.low, "normal": Importance.normal, "high": Importance.high}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _find_list(client: GraphClient, name: str) -> TodoTaskList:
    """Return the task list with the given name, or exit."""
    match = next((tl for tl in client.me.todo.lists.get().execute_query() if tl.display_name == name), None)
    if match is None:
        print(f"No task list named '{name}'. Create one with the 'add-list' subcommand.")
        sys.exit(1)
    return match


def _find_task(task_list: TodoTaskList, task_id: str) -> TodoTask:
    """Return a task by id, or exit."""
    task = next((t for t in task_list.tasks.get().execute_query() if t.id == task_id), None)
    if task is None:
        print(f"No task with id '{task_id}' in list '{task_list.display_name}'.")
        sys.exit(1)
    return task


def cmd_lists(client: GraphClient, args: argparse.Namespace) -> None:
    lists = client.me.todo.lists.get().execute_query()
    print(f"Task lists: {len(lists)}")
    for tl in lists:
        tasks = tl.tasks.get().execute_query()
        print(f"  {tl.id:40s} {tl.display_name:30s} ({len(tasks)} tasks)")


def cmd_tasks(client: GraphClient, args: argparse.Namespace) -> None:
    task_list = _find_list(client, args.list_name)
    tasks = task_list.tasks.get().execute_query()
    print(f"Tasks in '{task_list.display_name}' ({len(tasks)}):")
    for t in tasks:
        due = t.due_date_time
        print(f"  {t.id:40s} {t.status.value if t.status else '?':12s} {t.title or '?':35s} due={due}")


def cmd_add_list(client: GraphClient, args: argparse.Namespace) -> None:
    task_list = client.me.todo.lists.add(args.name).execute_query()
    print(f"✓ Task list created: {task_list.display_name} ({task_list.id})")


def cmd_add_task(client: GraphClient, args: argparse.Namespace) -> None:
    task_list = _find_list(client, args.list_name)
    due = datetime.now(timezone.utc) + timedelta(days=args.due_in) if args.due_in else None
    task = task_list.tasks.add(
        title=args.title,
        due_date_time=due,
        importance=IMPORTANCE.get(args.importance) if args.importance else None,
        body=args.body,
    ).execute_query()
    print(f"✓ Task created: {task.title} ({task.id})")


def cmd_checklist(client: GraphClient, args: argparse.Namespace) -> None:
    task_list = _find_list(client, args.list_name)
    task = _find_task(task_list, args.task_id)
    if args.add:
        item = task.checklist_items.add(displayName=args.add, isChecked=False).execute_query()
        print(f"✓ Checklist item added: {item.display_name} ({item.id})")
        return
    items = task.checklist_items.get().execute_query()
    print(f"Checklist items on '{task.title}' ({len(items)}):")
    for item in items:
        state = "checked" if item.is_checked else "unchecked"
        print(f"  {item.id:40s} {item.display_name or '?':30s} {state}")


def cmd_complete(client: GraphClient, args: argparse.Namespace) -> None:
    task_list = _find_list(client, args.list_name)
    task = _find_task(task_list, args.task_id)
    task.status = TaskStatus.completed
    task.update().execute_query()
    print(f"✓ Task completed: {task.title}")


def cmd_delete_list(client: GraphClient, args: argparse.Namespace) -> None:
    task_list = _find_list(client, args.name)
    task_list.delete_object().execute_query()
    print(f"✓ Task list deleted: {task_list.display_name}")


def _add_list_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--list", dest="list_name", required=True, help="name of the task list")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Microsoft To Do tasks")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("lists", help="list task lists")
    p.set_defaults(func=cmd_lists)

    p = sub.add_parser("tasks", help="show tasks in a list")
    _add_list_arg(p)
    p.set_defaults(func=cmd_tasks)

    p = sub.add_parser("add-list", help="create a task list")
    p.add_argument("--name", required=True, help="task list display name")
    p.set_defaults(func=cmd_add_list)

    p = sub.add_parser("add-task", help="create a task")
    _add_list_arg(p)
    p.add_argument("--title", required=True, help="task title")
    p.add_argument("--due-in", type=int, default=None, help="days from now until the task is due")
    p.add_argument("--importance", choices=sorted(IMPORTANCE), default=None, help="task importance")
    p.add_argument("--body", default=None, help="task body text")
    p.set_defaults(func=cmd_add_task)

    p = sub.add_parser("checklist", help="list or add checklist items on a task")
    _add_list_arg(p)
    p.add_argument("--task", dest="task_id", required=True, help="task id")
    p.add_argument("--add", default=None, help="display name of a checklist item to add")
    p.set_defaults(func=cmd_checklist)

    p = sub.add_parser("complete", help="mark a task as completed")
    _add_list_arg(p)
    p.add_argument("--task", dest="task_id", required=True, help="task id")
    p.set_defaults(func=cmd_complete)

    p = sub.add_parser("delete-list", help="delete a task list")
    p.add_argument("--name", required=True, help="task list display name")
    p.set_defaults(func=cmd_delete_list)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(_client(), args)


if __name__ == "__main__":
    main()
