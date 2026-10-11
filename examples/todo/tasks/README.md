# Tasks

A `todoTask` is the unit of work. Beyond a title it has a body, an importance
(`low` / `normal` / `high`), a status (`notStarted`, `inProgress`, `completed`,
`waitingOnOthers`, `deferred`), start / due / reminder date-times, categories,
and an optional recurrence.

## [Task lifecycle](lifecycle.py)

Creates a task with a due date, importance, categories, start date, and an
optional recurrence; renames and reprioritises it; completes and reopens it; and
cleans up unless `--keep`.

```python
task = task_list.tasks.add(
    "Write the sprint plan",
    due_date_time=datetime.now(timezone.utc) + timedelta(days=2),
    importance=Importance.high,
).execute_query()
task.status = TaskStatus.completed
task.update().execute_query()
```

## [Search tasks](query.py)

Builds an OData `$filter` from the command line and prints the matches sorted by
due date, importance, or title. Scans every list unless `--list` is given —
the script for "what is overdue?" and "what is due this week?".

```python
tasks = task_list.tasks.filter("status ne 'completed' and dueDateTime/dateTime lt '…'").get().execute_query()
```

!!! note "DateTime literals"
    The date-time part of a To Do filter is `dueDateTime/dateTime` and its value
    must be **quoted**: `dueDateTime/dateTime lt '2026-05-01T00:00:00.0000000Z'`.
    Note that such a bound also matches tasks **without** a due date, and
    `dueDateTime ne null` is unsupported, so `query.py` always adds a lower bound.

## [Checklist subtasks](checklist.py)

Adds a checklist to a task, ticks one item, renames another, and deletes a
third. A `checklistItem` has only a `displayName` and an `isChecked` flag.

```python
task.checklist_items.add(displayName="Collect the numbers").execute_query()
```

All three need the delegated permission **`Tasks.ReadWrite`**.
