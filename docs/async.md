# Async / await

!!! note "Sync by default, async opt-in"

    The synchronous API is the default and is unchanged; async is additive and
    shares the same context. Lifecycle hooks (`before_execute`, `after_execute`,
    `on_error`) are synchronous — do the work after `await`ing the terminal.

Run the same fluent API from `async` code. Builders stay synchronous — only the
terminal calls that hit the network gain an `_async` twin that you `await`:

| Synchronous | Asynchronous |
|---|---|
| `ctx.execute_query()` | `await ctx.execute_query_async()` |
| `obj.execute_query()` | `await obj.execute_query_async()` |
| `ctx.execute_query_retry()` | `await ctx.execute_query_async_retry()` |
| `ctx.execute_query_with_incremental_retry()` | `await ctx.execute_query_with_incremental_retry_async()` |
| `ctx.execute_query_parallel()` | `await ctx.execute_query_parallel_async()` |
| `ctx.execute_batch()` | `await ctx.execute_batch_async()` |
| `obj.execute_batch()` | `await obj.execute_batch_async()` |
| `result.execute_query_retry()` | `await result.execute_query_async_retry()` |
| `ctx.execute_request_direct(path)` | `await ctx.execute_request_direct_async(path)` |
| `collection.get_all()` | `await collection.get_all_async()` |
| `collection.export_to(path, page_size=n)` | `await collection.export_to_async(path, page_size=n)` |
| `for item in collection` | `async for item in collection` |
| `folder.download(dir).execute_query()` | `await folder.download(dir).execute_query_async()` |
| `file.download_session(stream)` | `await file.download_session_async(stream)` |
| `drive_item.download_session(stream)` | `await drive_item.download_session_async(stream)` |
| `drive_item.resumable_upload(path)` | `await drive_item.resumable_upload_async(path)` |
| `files.create_upload_session(path, size)` | `await files.create_upload_session_async(path, size)` |
| `result.execute_batch()` | `await result.execute_batch_async()` |

No extra dependency is required. By default the blocking HTTP call is handed to
a worker thread, so the event loop stays free and existing transports (session,
auth, proxies, rate limiting) are reused unchanged.

## Quick start

```python
import asyncio

from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(site_url).with_username_and_password(tenant, client_id, username, password)


async def main() -> None:
    web = await ctx.web.get().execute_query_async()
    print(web.title)


asyncio.run(main())
```

`execute_query_async()` returns the same object as its synchronous twin, so the
patterns you already use (`await ctx.web.get().execute_query_async()`, reading
`.value`, chaining) are unchanged.

## Concurrency

A context drains its own pending query queue on every call. To run independent
requests concurrently, give each one its own [cloned](getting-started.md) context
(the clone shares credentials and the connection pool) and await them together:

```python
web_ctx = ctx.clone(site_url)
lists_ctx = ctx.clone(site_url)

web, lists = await asyncio.gather(
    web_ctx.web.get().execute_query_async(),
    lists_ctx.web.lists.get().execute_query_async(),
)
```

For many queued operations, prefer the batch API below — it overlaps batches
without hand-managing contexts.

### Parallel queries on one context

When you have queued several **independent** requests (e.g. a metadata read per
file), drain them together with `execute_query_parallel_async()`. It overlaps the
network round-trips with bounded concurrency and per-query retry, so you don't
need clones, a `Semaphore`, or `as_completed`:

```python
def report(progress):
    print(f"{progress.stage}: {progress.done}/{progress.total}")


folder = ctx.web.get_folder_by_server_relative_url("/sites/contoso/Shared Documents")
files = await folder.files.get().execute_query_async()
for file in files:
    file.ensure_property("Length")  # queue one read per file

await ctx.execute_query_parallel_async(concurrency=6, progress=report)
```

It is the `await` twin of `execute_query_parallel()`, with the same
`concurrency`/`progress`/`max_retry` arguments. It routes each request through
the configured async transport, so it also drives the optional `httpx` engine
below.

Both forms take an optional keyword-only `on_error=(query, error) -> None`
collector: when supplied, a permanently failing query is reported to it and
skipped instead of aborting the batch (this is what bulk downloads use to
continue-and-report). Without it, the first permanent failure raises as before.

For downloads specifically you don't need this primitive directly — use the
high-level API below.

## Download

Downloading a folder, a file collection, or a single file is a builder + terminal
pair like every other query, so one name gives you both forms:

```python
# asynchronous
op = folder.download("/data/docs")
await op.execute_query_async(concurrency=8)

# synchronous — same builder
op = folder.download("/data/docs")
op.execute_query()
```

Like every other terminal, `execute_query()` / `await execute_query_async()`
return the operation itself; the outcome is on `op.value`.

`folder.download(target_dir)` enumerates the folder (paged, recursive by
default), preserves the relative tree under `target_dir`, and downloads the files
with bounded concurrency and per-file retry. `files.download(target_dir)`
downloads one collection flat; `file.download(path)` downloads a single file.
No streams, no `ExitStack`, no handle bookkeeping — the operation opens and
closes each destination itself.

Domain intent stays on the builder; execution knobs stay on the terminal:

| Builder (`download`) | Terminal (`execute_query` / `execute_query_async`) |
|---|---|
| `target_dir`, `recursive`, `overwrite`, `resume`, `progress` | `concurrency`, `max_retry`, `timeout_secs`, `max_delay`, `jitter` |

`op.value` is a `DownloadResult`:

```python
op = folder.download("/data/docs")
op.execute_query(concurrency=8)
result = op.value
print(result.success, result.skipped, result.errors)
for file, error in result.failures:
    print("failed", file.server_relative_url, error)
```

- **Resumable by default** — `overwrite=False` skips files that already exist, so
  re-running continues where it stopped. Pass `overwrite=True` to replace.
- **Resume partial files** — with `resume=True`, an existing destination smaller
  than the remote file is completed by fetching only the missing byte range
  (HTTP `Range`) and appending it, so an interrupted large download is not
  restarted from scratch. A destination at least as large as the remote file is
  treated as complete and skipped; servers that ignore the range (a `200` with
  the full body) still produce a correct file.
- **Continue-and-report** — a permanently failing file is collected in
  `result.failures` (and counted in `result.errors`); the rest keep downloading.
  Call `result.raise_if_errors()` to opt back into fail-fast.
- **Progress** — `progress` receives `Progress` snapshots: `stage="scanning"`
  while enumerating, `stage="downloading"` with `done`/`total` while transferring.

Under the hood this is the builder form of the parallel primitive above: it
queues one `get_content()` per file and drains it with
`execute_query_parallel(_async)`, bound to the destination paths.

### Streaming large files

`file.download(path)` buffers each file in memory before writing it. For large
files, open the destination yourself and use `download_session_async()`: it
streams the body chunk by chunk through the async transport (native with
`httpx`, otherwise a worker thread), so the content is never buffered and the
event loop never blocks:

```python
with open("/data/big.iso", "wb") as stream:
    await file.download_session_async(
        stream,
        chunk_size=1024 * 1024,
        progress=lambda p: print(p.done, p.total),
    )
```

The synchronous `file.download_session(stream)` is the twin; both accept
`chunk_downloaded(bytes_so_far)`, `chunk_size`, `use_path` and `progress`. The
awaitable form ensures the addressing property is loaded first and raises the
same `ClientRequestException` on failure as the rest of the async API.

When the body is going somewhere other than a local file — a second upload, a
`socket`, a hash — use the async generator `get_content_stream_async()`. It
yields the same stream chunk by chunk and closes the HTTP response when you stop
early:

```python
import hashlib

digest = hashlib.sha256()
async for chunk in item.get_content_stream_async(chunk_size=1024 * 1024):
    digest.update(chunk)
print(digest.hexdigest())
```

Graph `DriveItem` and SharePoint `File` both expose it (`File` also takes
`use_path=`); an optional `on_headers=` callback receives the response headers
before the first chunk, e.g. to read `Content-Length`.

### Uploading large files

For files above the 4 MB simple-upload limit, OneDrive/Graph require an upload
session. `resumable_upload_async()` is the awaitable twin of
`resumable_upload()`: it creates the session and sends every chunk before it
returns, reading each chunk from disk on the offload executor and PUT-ing it
through the async transport, so a multi-gigabyte upload keeps the event loop
free:

```python
folder = client.me.drive.root
item = await folder.resumable_upload_async(
    "/data/big.iso",
    chunk_size=320 * 1024 * 5,  # Graph requires a multiple of 320 KiB
    progress=lambda p: print(p.percent),
)
print(item.web_url)
```

Chunks are still uploaded **sequentially** (the service requires ordered
ranges); only the disk read and the HTTP send move off the loop. Both
`chunk_uploaded(bytes_uploaded)` and `progress` (`stage="uploading"`) are
supported, and a failure raises the same `ClientRequestException` as the rest of
the async API (or is dispatched to a registered `onError` handler).

SharePoint document libraries use a different upload-session protocol;
`FileCollection.create_upload_session_async()` is the awaitable twin of
`create_upload_session()` and keeps the same `chunk_uploaded`/`progress`
behavior:

```python
folder = ctx.web.get_folder_by_server_relative_url("/sites/dev/Shared Documents")
await folder.files.create_upload_session_async(
    "/data/big.iso",
    chunk_size=4 * 1024 * 1024,
    progress=lambda p: print(f"{p.done}/{p.total}"),
)
```

## Recipes

End-to-end examples that show where async pays off:

- [Audit every site collection concurrently](products/patterns/async/tenant_site_audit.md) —
  bounded fan-out over a tenant, replacing an N+1 sequential loop.
- [Download a library concurrently](products/patterns/async/download_library_async.md) —
  progress as each file finishes, per-file retry.
- [Bulk-update list items](products/patterns/async/bulk_update_async.md) —
  `execute_batch_async` sends the batches in parallel.
- [Show the current user](products/sharepoint/users/whoami_async.md) — the
  minimal async query, the `await` twin of `whoami.py`.

## Batch

`execute_batch_async()` splits pending changes exactly like `execute_batch()` and
sends each batch through the configured async transport (native if one is set,
otherwise a worker thread), so the loop is never blocked. Only the
transiently-failed sub-requests are resent, honoring `Retry-After`. With
`concurrency` > 1 the batches overlap:

```python
target_list = ctx.web.lists.get_by_title("Company Tasks")
for index in range(250):
    target_list.add_item({"Title": f"Task {index}"})

await ctx.execute_batch_async(items_per_batch=100, concurrency=4)
```

Graph's JSON batch keeps its `sequential=True` option (chained `dependsOn`)
exactly as the synchronous method:

```python
await client.execute_batch_async(items_per_batch=20, sequential=True)
```

### Batch vs long-running operations

Two different ideas, easy to confuse:

- **Batch** packs many independent short requests into one HTTP round-trip
  (SharePoint `$batch` / Graph JSON batch). It is about *how many requests* travel
  together — use it for bulk creates, updates and deletes.
- **Long-running operations (LRO)** are a *single* request the service accepts
  with `202 Accepted` and finishes later — copying a large drive item, cloning a
  team, a workbook recalculation. The response carries a monitor URL that you poll
  with `wait()` / `wait_async()` (or an operation entity you `await` directly).

Batching an LRO does **not** wait for it: the `202` comes back inside the batch
and you still have to poll. Keep LROs out of a batch and await them individually:

```python
result = source.copy(name="copy.xlsx", parent=dest).execute_query()
status = await result.wait_async()  # polls the monitor URL off the loop
```

`wait_async()` is the event-loop twin of `wait()`; both honor the server's
`Retry-After`, back off on `429`/`503`, and support restartable continuation
tokens. See [Long-running operations](long-running-operations.md) for the poller,
the `Prefer: respond-async` submissions and the Graph operation entities.

## Paging

`get_all_async()` is the awaitable twin of `get_all()`: it follows
server-driven paging (`@odata.nextLink`, or the SharePoint `$skip` fallback)
until the collection is exhausted, without blocking the loop:

```python
files = ctx.web.get_folder_by_server_relative_url("/sites/contoso/Shared Documents").files
await files.get_all_async(page_size=2000, progress=lambda p: print(p.done))
for file in files:
    print(file.name)
```

Collections are also async iterables, so you can stream page by page without
loading everything first — the first page is fetched on demand and each
remaining page is awaited as it is reached:

```python
files = ctx.web.get_folder_by_server_relative_url("/sites/contoso/Shared Documents").files.paged(2000)
async for file in files:
    print(file.name)
```

Both forms reuse `progress` / `page_loaded` and follow the same server-driven
paging (`@odata.nextLink`, or the SharePoint `$skip` fallback) as the
synchronous `for file in collection`.

### Streaming export

`export_to_async()` is the awaitable twin of `export_to()`. With `page_size` it
streams an appendable format (CSV/TSV/NDJSON/JSON) page by page: each page is
fetched through the server paging and projected/written on the worker pool, so a
multi-million-row export stays memory-bounded and the loop stays free. The target
is flushed and closed even if the export is cancelled or a page fails.

```python
# SharePoint list
await ctx.web.lists.get_by_title("Company Tasks").export_to_async("tasks.csv", page_size=2000)

# Graph collection — the same API on any RecordCollection
await client.users.select(["id", "displayName", "mail"]).export_to_async("users.csv", page_size=500)
```

Without `page_size` the already-loaded items are written in a single offloaded
pass; pair it with `await collection.get_all_async()` first.

### Repeated rows and `$top`

Two paging caveats worth knowing:

- **`$top` can suppress the next link.** On some Graph endpoints an explicit
  `$top` (the `.top(n)` builder) makes the service return a single page and omit
  `@odata.nextLink`, so an otherwise complete `get_all()` stops early. To read
  everything, drive the page size with `page_size=` / `paged(page_size)` and let
  the library follow the links, instead of capping the whole query with `$top`.
- **A service can repeat rows across pages.** Graph directory-export APIs are
  known to return the same item on two consecutive pages during a service
  update. Pass `dedupe_by="id"` to `get_all()` / `get_all_async()` to keep only
  the first occurrence of each value. De-duplication runs after the last page
  loads, so it never disturbs the `$skip` offsets:

  ```python
  users = ctx.users
  await users.get_all_async(page_size=200, dedupe_by="id")
  ```

## Throttling

Async requests share the exact same pacing gate as synchronous ones. When a
context is configured with `with_rate_limit(...)`, the gate is awaited on the
event loop (`RateLimiter.acquire_async`) and every response — including each
sub-response of a batch — is observed, so concurrent async tasks ease off
together instead of blocking a worker thread.

## Retry

`execute_query_async_retry()` mirrors `execute_query_retry()` but waits between
attempts with `asyncio.sleep`, so other tasks keep running:

```python
await ctx.execute_query_async_retry(max_retry=5, timeout_secs=5, max_delay=60)
```

The retry policy mirrors `execute_query_retry` exactly: transient errors
(408/429/5xx and connection errors) are retried with exponential backoff and
jitter. Pass a `failure_callback` (for example returning the server's
`Retry-After` via `retry_after_delay`) to override the backoff.

For a context-wide policy, `with_auto_retry(...)` makes **every**
`execute_query_async` retry transient failures, so you don't opt in at each call
site:

```python
ctx.with_auto_retry(max_retry=5, max_delay=60)
await ctx.me.get().execute_query_async()
```

## Credentials

A token callback registered with `with_access_token` may be an ordinary function
or an `async def`. The async API awaits an async callback on the event loop — no
worker thread, no loop stall — so token acquisition can use genuinely
asynchronous I/O; synchronous callbacks keep their existing offload behaviour:

```python
async def token_callback() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(token_url) as resp:
            return await resp.json()


ctx = GraphClient(token_callback=token_callback)  # or ctx.with_access_token(...)
await ctx.me.get().execute_query_async()
```

Concurrent async requests share one acquisition (single-flight), and the token is
cached for its `expiresIn`, so the synchronous hooks that build a batch payload can
reuse it. A request authenticated on the loop is marked, so the offloaded
synchronous auth hook skips it rather than fetching a second token. Calling the
**synchronous** API while an async callback is configured raises a clear
`RuntimeError` instead of failing with an unreadable token.

## Async context manager

`ClientContext` can be used as an async context manager; on exit the transport is
closed without blocking the loop:

```python
async with ctx:
    web = await ctx.web.get().execute_query_async()
```

`__aexit__` awaits `ctx.aclose()`. If you don't use the context-manager form,
call the lifecycle methods yourself — `ctx.close()` for the synchronous transport
and `await ctx.aclose()` for the async one — so pooled connections are released
promptly instead of at interpreter shutdown:

```python
ctx = GraphClient(credentials)
try:
    ...
finally:
    await ctx.aclose()
```

## Cancellation

`await`s are cancellable: cancelling the task raises `asyncio.CancelledError`
into the awaiting coroutine. The async terminals leave the context consistent:

- `execute_query_parallel_async()` cancels its in-flight siblings and re-queues
  the queries that were not applied with the current cursor cleared, so a retry
  resumes cleanly.
- `get_content_stream_async()` and the streaming downloads close the HTTP
  response when the consumer breaks out of the loop or the task is cancelled, so
  the connection is not leaked.
- A streamed `export_to_async()` flushes and closes its target even on
  cancellation.

Wrap long transfers in a timeout when you want a hard bound (`asyncio.wait_for`
keeps a Python 3.8 floor):

```python
try:
    await asyncio.wait_for(file.download_session_async(stream), timeout=30)
except asyncio.TimeoutError:
    ...  # the response was closed for you
```

## Optional native-async transport

The default transport offloads blocking `requests` calls to a thread. If you
prefer genuinely asynchronous I/O, install the optional
[`httpx`](https://www.python-httpx.org/) extra and select it for the async path
only — synchronous calls keep using `requests`:

```bash
pip install office365-rest-python-client[httpx]
```

```python
from office365.runtime.transport.httpx_transport import HttpxTransport

ctx.pending_request().with_async_transport(HttpxTransport())
try:
    web = await ctx.web.get().execute_query_async()
finally:
    await ctx.pending_request().async_transport.aclose()
```

!!! note "Limits of the httpx transport"
    Responses are adapted to `requests.Response`, so downstream code is
    unchanged. Non-streaming bodies are read eagerly into memory; streamed
    downloads use the native `aiter_bytes` path and are never buffered. TLS
    verification, proxies and redirect policy are client-level constructor
    settings; per-request `verify` and `proxies` are not honored.

## Offload executor

With the default `requests` transport, the blocking work behind every `await`
(request send, streaming reads, `beforeExecute` auth/digest hooks) runs on a
worker pool owned by the library — not the event loop's shared default executor.
That keeps heavy HTTP traffic from starving other loop callbacks and lets you
size the two pools independently.

The pool is created lazily on first use. Tune it *before* the first async
request:

```python
from office365.runtime.transport.offload import configure_offload_executor

configure_offload_executor(max_workers=16, thread_name_prefix="o365-http")
```

- `max_workers=None` (default) uses `min(32, os.cpu_count() + 4)`.
- Configuring after the pool exists raises `RuntimeError`; call
  `shutdown_offload_executor()` to release it and restore defaults first.
- An individual transport can opt out of the shared pool by setting its own
  executor, e.g. `transport.offload_executor = my_executor`. The executor must
  outlive the transport.
- The native-async `httpx` transport does not use this pool: its requests run on
  the loop.

Each session the default transport creates has its own `requests` connection
pool. When many requests hit the same host concurrently, size the pool to match:

```python
ctx.with_transport(pool_connections=10, pool_maxsize=32)
```

`with_transport` accepts `pool_connections`, `pool_maxsize` and `pool_block`
(also on `RequestsTransport`). They are ignored when you pass your own
`session=` — that session's adapters are yours to configure.

## Notes

- Async support is additive: nothing in the synchronous API changed, and both
  paths can share one context. Builders remain synchronous; call them before
  `await`ing.
- The async batch path now sends through the request's async transport and
  retries only transiently-failed sub-requests, exactly like the synchronous
  path; it no longer offloads the whole synchronous batch. Blocking
  `beforeExecute` hooks (token acquisition, digest refresh) are offloaded to a
  worker thread so they cannot stall the loop; an async token callback (see
  [Credentials](#credentials)) is awaited on the loop instead.
- If an async parallel run is cancelled, its in-flight sibling requests are
  cancelled too, and the queries that were not applied are put back on the
  context's queue with the current query cleared, so a retry resumes cleanly. A
  cancelled sequential drain likewise re-queues the in-flight query.
- `retry_async()` and the async terminals are available from
  `office365.runtime.retry` and the usual query objects.
- The default `requests` transport is thread-safe: it keeps one `Session` per
  thread (each with its own connection pool), so parallel and offloaded async
  requests never share a session. Passing an explicit `session=` to
  `with_transport(...)` uses that single session as-is, making its thread safety
  the caller's responsibility.

See the runnable [async examples](products/patterns/async/index.md).
