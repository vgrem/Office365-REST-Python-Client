# Task lists

A `todoTaskList` is the container for tasks. Besides user-created lists there are
a few **well-known** lists (`defaultList`, `flaggedEmails`) that the service
manages; `wellknownListName` reports which is which, and `isOwner` / `isShared`
describe who owns and who can see a list.

## [Task list lifecycle](lifecycle.py)

Lists the existing lists, then creates a demo list with `ensure` (get-or-create
by display name), renames it, and deletes it again. Safe to re-run — it reuses
the list by name and cleans up unless `--keep`.

```python
task_list = client.me.todo.lists.ensure("Groceries").execute_query()
task_list.set_property("displayName", "Groceries (renamed)")
task_list.update().execute_query()
```

Needs the delegated permission **`Tasks.ReadWrite`**.
