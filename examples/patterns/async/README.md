# Async / await

Every query that reaches the network has an async twin: build the same fluent
query, then `await ...execute_query_async()` instead of blocking the thread.
Builders stay synchronous — only the terminal call changes. No extra dependency
is required: by default the blocking HTTP call is offloaded to a worker thread,
keeping the event loop free. An optional native-async transport (httpx) is also
available.

## Query

### [Show the current user asynchronously](../../sharepoint/users/whoami_async.py)

Same builder as the synchronous [whoami.py](../../sharepoint/users/whoami.py) —
only the terminal call is awaited:

```python
me = await ctx.web.current_user.get().execute_query_async()
```

### [Load a web asynchronously](load_web_async.py)

```python
web = await ctx.web.get().execute_query_async()
print(web.title)
```

### [Run queries concurrently](concurrent_requests.py)

A context drains its own pending queue on each call, so overlap independent
requests across cloned contexts:

```python
web, lists = await asyncio.gather(
    web_ctx.web.get().execute_query_async(),
    lists_ctx.web.lists.get().execute_query_async(),
)
```

For many independent requests queued on **one** context, use
`ctx.execute_query_parallel_async()` — it owns the bounded fan-out and per-query
retry, so no clones or semaphores are needed. For downloads specifically, skip
the primitive and use `folder.download(dir)` (see below).

## Recipes

### [Audit every site collection concurrently](tenant_site_audit.py)

Fan out one admin call per site with a `Semaphore`, removing the N+1 sequential
loop of the synchronous counterpart. Each task clones the context, so the run
shares one token and one connection pool:

```python
async with sem:
    clone = ctx.clone(admin_site_url)
    props = await Tenant(clone).get_site_properties_by_url(site.url).execute_query_async()
```

### [Download a library concurrently](download_library_async.py)

`folder.download` enumerates the folder (paged, recursive by default), preserves
the relative tree, skips files that already exist, and downloads with bounded
concurrency — one builder, one terminal, no streams or semaphores:

```python
op = root_folder.download(output_dir, progress=report)
await op.execute_query_async(concurrency=6)
result = op.value
print(result.success, result.skipped, result.errors, len(result.failures))
```

### [Export a large collection while the loop stays responsive](export_users_async.py)

`export_to_async(..., page_size=...)` follows server paging one page at a time
and projects/writes each page on the worker pool, so memory stays flat and other
tasks keep running — the example runs a heartbeat beside a nightly tenant export
to prove the loop never stalls:

```python
await client.users.select(["id", "displayName", "mail"]).export_to_async("users.csv", page_size=500)
```

The same call works on any `RecordCollection`, including SharePoint lists:

```python
await lst.export_to_async("tasks.csv", format="csv", page_size=2000)
```

### [Upload a large file with an upload session](upload_large_file_async.py)

Files above 4 MB need an upload session; the awaitable
`resumable_upload_async()` creates it and streams ordered chunks, reading each
from disk on the worker pool, so a multi-gigabyte upload keeps the loop free:

```python
item = await drive.root.resumable_upload_async(path, chunk_size=320 * 1024 * 5, progress=report)
print(item.web_url)
```

SharePoint libraries use `files.create_upload_session_async(path, size, progress=...)`
instead — same ordered-chunk loop, same `chunk_uploaded`/`progress` behavior.

### [Bulk-update list items](bulk_update_async.py)

Queue updates with synchronous builders, then let `execute_batch_async` send the
batches in parallel:

```python
await ctx.execute_batch_async(items_per_batch=100, concurrency=4, success_callback=on_batch)
```

### [Import a directory through a bounded pipeline](pipeline_import.py)

A producer feeds a bounded `asyncio.Queue`; worker tasks drain it, so disk reads
and uploads overlap while memory and connection usage stay flat:

```python
await queue.put((remote_name, path))  # producer blocks when the queue is full
clone = ctx.clone(site_url)  # one queue per worker
folder.upload_file(remote_name, content)
await clone.execute_query_async()
```

### [Cancel a parallel run and resume it](cancellation.py)

Cancelling `execute_query_parallel_async` re-queues the unapplied queries, so a
retry picks the work back up (at-least-once) instead of losing it:

```python
task.cancel()  # e.g. Ctrl-C or a timeout
# ... CancelledError ...
await ctx.execute_query_parallel_async()  # resumes the restored queries
```

### [Bulk-create under a shared rate limiter](rate_limited_bulk_create.py)

Opt in to fleet-wide pacing before a large write; `Retry-After` / high health
scores hold every request back as a group:

```python
ctx.with_rate_limit(health_threshold=80, min_interval=0.1)
await ctx.execute_batch_async(items_per_batch=50, concurrency=4)
```

## Integration

### [Bridge the library into FastAPI](fastapi_integration.py)

Await the terminal directly inside an ASGI handler; clone a shared context per
request so handlers never share a pending-query queue:

```python
@app.get("/users")
async def list_users(top: int = 10):
    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    users = await client.users.top(top).select(["id", "displayName"]).get().execute_query_async()
    return [{"id": u.id, "display_name": u.display_name} for u in users]
```

## Batch

### [Submit a batch asynchronously](batch_async.py)

```python
await ctx.execute_batch_async(items_per_batch=100, concurrency=4)
```

## Transports

### [Use the optional httpx transport](httpx_transport.py)

```python
ctx.pending_request().with_async_transport(HttpxTransport())
```

## Credentials

### [Acquire tokens with an async callback](token_callback_async.py)

`with_access_token` accepts an `async def`; the async API awaits it on the loop
(single-flight, cached until it expires), so a broker reached over async HTTP
never blocks the event loop:

```python
async def token_callback() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(broker_url) as resp:
            return await resp.json()


client = GraphClient(token_callback=token_callback)
users = await client.users.top(5).select(["id", "displayName"]).get().execute_query_async()
```

Pass an `async def` — a plain `lambda` that returns a coroutine is not detected
as async and would be treated as a synchronous callback. Calling the synchronous
API while an async callback is configured raises a clear `RuntimeError`.

## Long-running operations

Graph finishes some calls later: the request is accepted with `202 Accepted` and
a monitor URL you poll until the work reaches a terminal status. Every wait has
an async twin that yields to the loop between polls, so a copy or a team clone
never freezes concurrent tasks. See the **Long-running operations** page under
Guides for the full story.

### [Copy a large file and await it](../lro/copy_drive_item_async.py)

`copy()` returns a result that captures the monitor URL; `wait_for_item_async()`
polls it and resolves the new item:

```python
result = source.copy(name="big (copy).xlsx", parent=dest)
await result.execute_query_async()
copied = await result.wait_for_item_async(on_progress=lambda status: print(status.percentage_complete))
```

### [Clone a team and await provisioning](../lro/wait_team_clone_async.py)

`clone()` returns a `teamsAsyncOperation`; poll it off the loop, treating a
transient `404` as "not ready yet":

```python
operation = await source.clone(
    mail_nickname="clone1",
    display_name="Falcon",
    parts_to_clone=ClonableTeamParts.settings,
    visibility=TeamVisibilityType.private,
).execute_query_async()
await operation.poll_for_status_async(timeout_sec=600, polling_interval=15)
```

### [Poll a workbook operation](../lro/workbook_operation_async.py)

Opt into the async pattern with `Prefer: respond-async`; when the service accepts,
the result is awaitable, otherwise the query holds the synchronous answer:

```python
operation = await RespondAsyncRequest(ctx, query, wait=5).execute_async()
if operation is not None:
    await operation.wait_async()
```

### [Resume an operation from a continuation token](../lro/resume_from_token.py)

The monitor URL is the only state needed to resume, so persist it and pick the
operation back up in a later process:

```python
token = result.to_poller().to_continuation_token()
save(token.to_json())
# ... later, in another process ...
poller = OperationPoller.from_continuation_token(client, ContinuationToken.from_json(load()))
await poller.wait_async()
```

### [Guard against batching an LRO](../lro/lro_in_batch_guard.py)

Batching is for many short requests. A batched long-running operation loses its
monitor URL in the batch envelope, so this guard fails loudly instead of letting
the caller poll nothing — keep LROs out of a batch and await them individually.

### [Run a durable, resumable copy queue](../lro/copy_queue_worker_async.py)

The worker pattern behind "copy these 10,000 files": a bounded pool of copies
whose per-job continuation tokens are written to a JSON state file *before*
polling. A crash, a Ctrl-C or a deploy resumes the in-flight copies and skips
the completed ones instead of restarting:

```python
async with self._submit_lock:  # one request queue per context
    result = source.copy(name=job.name, parent=dest)
    await result.execute_query_async()
poller = result.to_poller()
await self._mark(job.key, token=poller.to_continuation_token().to_json())
await poller.wait_async(on_progress=report)  # polls overlap; submits are serialized
```

### [Provision many teams concurrently](provision_teams_async.py)

Submit every `teamsAsyncOperation`, then poll the whole batch through one bounded
parallel fan-out — no hand-rolled semaphore, and a bad row fails only its team:

```python
op.get()  # queue a status GET per unfinished operation
await client.execute_query_parallel_async(concurrency=8)
```

### [Archive files past a retention window](archive_old_files_async.py)

A retention job is copy → verify → delete, in that order. This one plans by
default and only mutates with `--apply`, so the destructive path is opt-in:

```python
status = await result.to_poller().wait_async()
copied = await client.me.drive.items[status.resource_id].get().execute_query_async()
if copied.size == item.size:  # verify before deleting the original
    await item.delete_object().execute_query_async()
```

### [Monitor migration jobs concurrently](../../sharepoint/migration/monitor/monitor_async.py)

The awaitable twin of the SharePoint migration monitor: each job gets its own
cloned context, and `monitor_async()` polls the progress API off the loop:

```python
await asyncio.gather(*(MigrationServerJob(ctx.clone(site_url).site).monitor_async(job_id) for job_id in job_ids))
```

## Reports

### [Stream a report while the loop stays responsive](export_report_async.py)

`reports.download_report_async()` follows the report's pre-authenticated URL
through the async transport and writes the CSV in chunks — never buffering it in
memory, never blocking the loop:

```python
result = await client.reports.download_report_async("getTeamsUserActivityUserDetail", "team.csv", "D30", progress=report)
```

## Streaming

### [Stream a file's content and hash it](stream_download_async.py)

`get_content_stream_async()` yields the body in chunks, so bytes go straight to a
hash, a socket or another upload; `on_headers` sees the response headers first:

```python
async for chunk in item.get_content_stream_async(chunk_size=1 << 20, on_headers=capture):
    hasher.update(chunk)
```

## Lifecycle & tuning

### [Manage the async client's lifecycle](client_lifecycle_async.py)

An async client owns a connection pool; the `async with` form awaits `aclose()` on
every exit path, and a long-lived client closes in `finally`:

```python
async with GraphClient(tenant=tenant).with_client_secret(client_id, client_secret) as client:
    users = await client.users.get_all_async(page_size=500)
```

### [Tune the offload executor](tune_offload_executor.py)

With the default `requests` transport, blocking sends run on a library-owned
thread pool. Size it *before* the first async request; afterwards
`configure_offload_executor()` raises `RuntimeError`:

```python
configure_offload_executor(max_workers=16, thread_name_prefix="o365-http")
# ... run work ...
shutdown_offload_executor()
```

### [Retry transient failures](retry_async.py)

`execute_query_async_retry()` retries the pending queries with jittered backoff
(honoring `Retry-After`); `retry_async()` wraps any awaitable that rebuilds its
query per attempt:

```python
users.get()
await client.execute_query_async_retry(max_retry=5, timeout_secs=2)
```

### [Page a large collection](page_users_async.py)

`get_all_async(page_size=...)` follows `@odata.nextLink` one page at a time:

```python
users = await client.users.select(["id", "displayName"]).get_all_async(page_size=500)
```

### [Sync incrementally with a delta token](delta_sync_async.py)

The delta feed returns only what changed since a cursor you persist:

```python
query = client.me.drive.root.delta
query = query.token(token) if token else query
changes = await query.get_all_async()
token = changes.delta_token
```

### [Upload a large file to SharePoint](upload_large_file_sp_async.py)

The awaitable `create_upload_session_async()` creates the file, uploads every
chunk and commits the last fragment before it returns:

```python
uploaded = await target.files.create_upload_session_async(path, chunk_size, progress=report)
```

### [Reuse an Entra ID token cache](entra_token_cache_async.py)

Hand `GraphClient` an MSAL `SerializableTokenCache` and persist it across runs so
repeat starts skip the full token exchange:

```python
client = GraphClient(tenant=tenant, token_cache=cache).with_client_secret(client_id, client_secret)
```

## Concurrency & best practices

- **One request per clone.** A context owns a single pending-query queue, so
  don't `await` two `execute_query_async()` calls on the same context at once.
  Use `ctx.clone(url)` per task: clones share credentials and the HTTP
  connection pool (one token, one session) but each has its own queue.
- **Drain many queued requests with the parallel terminal.** When the work is a
  list of independent queries (a `get()` per site), queue them and
  `await ctx.execute_query_parallel_async(concurrency=...)` — it bounds the
  fan-out and retries each query, so you don't manage clones or a `Semaphore`
  yourself. For downloads, use `folder.download(...)` (or `files.download(...)` /
  `file.download(path)`) instead — same engine, no stream management.
- **Bound the fan-out.** The default transport runs blocking calls on the event
  loop's thread pool (`min(32, os.cpu_count() + 4)` workers), so an unbounded
  `gather` over thousands of requests just queues. Size an `asyncio.Semaphore`
  (or the terminal's `concurrency`) to what the server will tolerate.
- **Isolate failures.** Prefer `asyncio.gather(..., return_exceptions=True)` or a
  per-task `try/except` so one failed item doesn't cancel the rest.
- **Retry transient errors.** Wrap terminals in `execute_query_async_retry()`
  (or configure a shared `RateLimiter`) when driving many requests at once.
- **Batch instead of hand-rolling.** For many queued writes,
  `execute_batch_async` overlaps batches for you — no cloning needed.
