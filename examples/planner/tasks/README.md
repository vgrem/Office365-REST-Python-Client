# Tasks

A **task** is a unit of work inside a plan. It can sit in a **bucket**, carry a
due date, a priority (`0` = urgent … `10` = low) and a percent complete, and be
assigned to one or more users. Each task also has a **details** object holding
the description and checklist. Requires **`Tasks.ReadWrite`**.

## Create, update and complete

```python
task = plan.tasks.add("Draft proposal", bucket=bucket).execute_query()
task.priority = 3
task.due_date_time = datetime.now(timezone.utc) + timedelta(days=7)
task.percent_complete = 25
task.update().execute_query()
```

→ [`lifecycle.py`](./lifecycle.py)

## Assign and unassign

The `assignments` map is keyed by user id. `assign_to` and `unassign` mutate it in
place, and `update()` sends the change (removal is sent as `null`):

```python
task.assign_to(client.me.get().execute_query()).update().execute_query()
task.unassign(me).update().execute_query()
```

→ [`assignments.py`](./assignments.py)

## Description and checklist

The task details hold the free-text description and the checklist. Checklist
items are keyed by a client-generated id; PATCH merges the map, so removing an
item means sending `null` for its id — `set_checklist([...])` replaces the whole
list for you.

```python
details = task.details.get().execute_query()
details.description = "Write the first draft."
details.add_checklist_item("Outline", is_checked=True).add_checklist_item("Review")
details.update().execute_query()
```

→ [`details.py`](./details.py)

## Query

`$select` is honoured, but `$filter`, `$orderby` and `$top` are ignored on a
plan's tasks — filter and sort in Python, or look a task up with `find_by_title`:

```python
rows = plan.tasks.select(["id", "title", "percentComplete"]).get().execute_query()
open_tasks = sorted((t for t in rows if t.percent_complete < 100), key=lambda t: t.priority)
task = plan.tasks.find_by_title("Draft proposal").execute_query()
```

→ [`query.py`](./query.py)

## Progress dashboard

[`progress_report.py`](./progress_report.py) is read-only: it walks your plans and
prints a per-task and aggregate progress breakdown.
