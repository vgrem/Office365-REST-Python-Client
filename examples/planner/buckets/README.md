# Buckets

A **bucket** is a column on the board ("Backlog", "In Progress", "Done"). It
belongs to a plan and tasks are placed in it. Requires **`Tasks.ReadWrite`** (or
`Group.ReadWrite.All`).

## Add, rename, look up and delete

Buckets are listed through the plan, but created and addressed on the top-level
`/planner/buckets` set — the library routes both for you:

```python
bucket = plan.buckets.add("Backlog").execute_query()
bucket.name = "Backlog (renamed)"
bucket.update().execute_query()

backlog = plan.buckets.find_by_name("Backlog (renamed)").execute_query()
if backlog.is_loaded:
    backlog.delete_object().execute_query()
```

`find_by_name` matches on the client, because Graph ignores `$filter` on a plan's
buckets and refuses to list `/planner/buckets` at all.

→ [`lifecycle.py`](./lifecycle.py)
