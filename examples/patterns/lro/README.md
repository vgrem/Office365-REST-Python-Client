# Long-running operations

Microsoft Graph answers some calls with **`202 Accepted`** and a *monitor* URL —
copying a large file, cloning a team, recalculating a workbook. The library hides
the polling loop behind three levels of help, all built on
`office365.runtime.lro`; see [Long-running operations](https://github.com/vgrem/office365-rest-python-client/blob/main/docs/long-running-operations.md)
for the full model.

| Level | Example | What it shows |
|---|---|---|
| Wait (blocking) | [`copy_and_wait.py`](./copy_and_wait.py) | `result.wait_for_item()` polls and returns the new item |
| Wait (async) | [`copy_drive_item_async.py`](./copy_drive_item_async.py) | the same, awaited, with a live percentage |
| Resume later | [`resume_from_token.py`](./resume_from_token.py) | persist a `ContinuationToken`, resume in a fresh process |
| **Monitor CLI** | [`monitor_cli.py`](./monitor_cli.py) | poll a token/URL from the shell; `--json`; exit 0/1/2 as a CI gate or cron watchdog |
| Durable queue | [`copy_queue_worker_async.py`](./copy_queue_worker_async.py) | a resumable async worker over many copies |
| Operation entities | [`wait_team_clone_async.py`](./wait_team_clone_async.py), [`workbook_operation_async.py`](./workbook_operation_async.py) | poll an operation *resource* (`TeamsAsyncOperation`, `WorkbookOperation`) |
| Gotcha | [`lro_in_batch_guard.py`](./lro_in_batch_guard.py) | a batched LRO loses its monitor URL — detect and reject it |

Requires the permission of the underlying operation (e.g. `Files.ReadWrite` for a
copy, `Team.Create`/`Team.ReadWrite.All` for a clone).

https://learn.microsoft.com/en-us/graph/long-running-actions-overview
