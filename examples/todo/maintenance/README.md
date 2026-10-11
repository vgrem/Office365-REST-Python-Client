# Maintenance

Housekeeping for a To Do account: removing the completed tasks that accumulate
over time.

## [Cleanup](cleanup.py)

Scans every list (or one with `--list`) for tasks completed more than `--days`
ago and deletes them. It is a **dry run by default** — nothing is removed until
you pass `--apply`.

```python
stale = [
    task
    for task in task_list.tasks.filter("status eq 'completed'").get().execute_query()
    if _completed_at(task) < cutoff
]
```

Needs the delegated permission **`Tasks.ReadWrite`**.
