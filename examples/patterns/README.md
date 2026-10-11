# Patterns

Cross-cutting *mechanisms* reused across every product, as opposed to the
product folders (`onedrive/`, `teams/`, `outlook/`, …) which are organized by
*resource*. Reach here once "what can I do?" is answered and the question becomes
"how do I do it reliably?".

| Group | Covers |
|---|---|
| [`lro/`](./lro/) | **Long-running operations** — wait (sync/async), resume from a token, a monitor CLI |
| [`async/`](./async/) | Async twins, concurrency, batching, streaming exports, credentials, transports |
| [`large-data/`](./large-data/) | Resumable chunked uploads, concurrent downloads, streamed exports |
| [`odata-query/`](./odata-query/) | `$select` / `$filter` / `$orderby` / `$top` / `$expand` on any collection |
| [`discovery/`](./discovery/) | Delta change tracking and tenant-wide search |
| [`reliability/`](./reliability/) | Error responses, throttling, retries |

Each folder has its own `README.md` with a "which example to use" guide.
