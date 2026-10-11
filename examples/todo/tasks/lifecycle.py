"""
Task lifecycle — create, update, complete, reopen, and delete a task.

A ``todoTask`` carries more than a title: a due date, start date, importance,
body, categories, a reminder, and an optional recurrence. This script walks the
whole lifecycle of one task, printing it at every step, and cleans up unless
``--keep`` is given.

    python lifecycle.py
    python lifecycle.py --title "Water the plants" --due-in 3 --importance high --repeat weekly

Requires delegated permission ``Tasks.ReadWrite`` for the signed-in user.

https://learn.microsoft.com/en-us/graph/api/resources/todotask
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.dayofweek import DayOfWeek
from office365.outlook.mail.importance import Importance
from office365.outlook.mail.patterned_recurrence import PatternedRecurrence
from office365.outlook.mail.recurrence_pattern import RecurrencePattern
from office365.outlook.mail.recurrence_range import RecurrenceRange
from office365.outlook.mail.recurrencepatterntype import RecurrencePatternType
from office365.outlook.mail.recurrencerangetype import RecurrenceRangeType
from office365.runtime.client_request_exception import ClientRequestException
from office365.todo.tasks.taskstatus import TaskStatus
from tests.settings import client_id, password, tenant, username

LIST_NAME = "SDK Tasks Demo"
PERMISSION_CODES = {"accessDenied", "Authorization_RequestDenied", "ErrorAccessDenied", "Forbidden"}
_REPEAT_TYPES = {
    "daily": RecurrencePatternType.daily,
    "weekly": RecurrencePatternType.weekly,
    "monthly": RecurrencePatternType.absoluteMonthly,
    "yearly": RecurrencePatternType.absoluteYearly,
}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _recurrence(kind: str, start: date) -> PatternedRecurrence:
    pattern = RecurrencePattern(type=_REPEAT_TYPES[kind], interval=1)
    if kind == "weekly":
        pattern.daysOfWeek.add(DayOfWeek(start.strftime("%w")))
    elif kind == "monthly":
        pattern.dayOfMonth = start.day
    elif kind == "yearly":
        pattern.dayOfMonth = start.day
        pattern.month = start.month
    recurrence_range = RecurrenceRange(type=RecurrenceRangeType.noEnd, startDate=start)
    return PatternedRecurrence(pattern=pattern, range=recurrence_range)


def _summarize(task) -> str:
    importance = task.importance.name if task.importance else "-"
    status = task.status.name if task.status else "-"
    due = task.due_date_time.dateTime or "-"
    return f"title={task.title!r} status={status} importance={importance} due={due}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Microsoft To Do task lifecycle")
    parser.add_argument("--title", default="Write the sprint plan", help="task title")
    parser.add_argument("--due-in", type=int, default=2, help="due in this many days (default: 2)")
    parser.add_argument(
        "--importance", choices=[item.name for item in Importance], default="high", help="task importance"
    )
    parser.add_argument("--categories", nargs="*", default=["Work"], help="category labels")
    parser.add_argument("--repeat", choices=[*_REPEAT_TYPES, "none"], default="none", help="recurrence pattern")
    parser.add_argument("--keep", action="store_true", help="keep the list and task instead of deleting them")
    args = parser.parse_args()

    client = _client()
    try:
        task_list = client.me.todo.lists.ensure(LIST_NAME).execute_query()

        now = datetime.now(timezone.utc)
        start = now + timedelta(hours=1)
        extra = {"startDateTime": DateTimeTimeZone.parse(start), "categories": args.categories}
        if args.repeat != "none":
            extra["recurrence"] = _recurrence(args.repeat, start.date())

        task = task_list.tasks.add(
            args.title,
            due_date_time=now + timedelta(days=args.due_in),
            importance=Importance[args.importance],
            body="Draft the goals, then share with the team.",
            **extra,
        ).execute_query()
        print(f"Created: {_summarize(task)}")
        if args.repeat != "none":
            print(f"         repeats {args.repeat}")

        task.title = f"{args.title} (v2)"
        task.set_property("importance", Importance.normal)
        task.update().execute_query()
        print(f"Updated: {_summarize(task)}")

        task.status = TaskStatus.completed
        task.set_property("completedDateTime", DateTimeTimeZone.parse(datetime.now(timezone.utc)))
        task.update().execute_query()
        print(f"Completed: {_summarize(task)}")

        task.status = TaskStatus.notStarted
        task.set_property("completedDateTime", None)
        task.update().execute_query()
        print(f"Reopened: {_summarize(task)}")

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
