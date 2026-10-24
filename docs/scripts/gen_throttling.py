"""Generate the throttling guide + quotas table (mkdocs-gen-files plugin).

The table is derived from the **catalogs** (`office365.limits.catalog`), so it can't
drift from the declarations, and its **Bound at** column is scanned from the `@limit`
decorators on the model. mkdocs-gen-files executes this module with ``runpy``, so
emission happens at module level.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import mkdocs_gen_files  # noqa: E402
from _limit_bindings import bound_at, row_attrs, scan_bindings  # noqa: E402
from office365.limits import Limit, catalog, catalog_products  # noqa: E402

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

_HEADER = """# Throttling

Microsoft Graph and SharePoint both throttle with **HTTP 429** and a
`Retry-After` header; Graph also reports how close an app is to its limit. The
library reads these signals, retries with the server's delay (falling back to
exponential backoff with jitter) and can pace a whole fleet proactively.

Unlike SharePoint's static [service limits](limits.md), Graph throttling is
**dynamic** — evaluated per scope (per app, per tenant, per app + tenant, per
resource) and per request type — so the library reacts to the signals rather
than enforcing a fixed budget. The quotas below are still declared as data (one
`quotas` module per product, plus the one row no product owns) so a workload can
be designed from the numbers instead of discovered by being throttled.

## Signals

| Header | Direction | Meaning |
| --- | --- | --- |
| `Retry-After` | response | Seconds to wait before retrying a 429/503 |
| `x-ms-throttle-limit-percentage` | response | Share of the limit consumed (`0.8`–`1.8`); `>= 1.0` means throttling |
| `x-ms-resource-unit` | response | The cost of this request (Identity resource units) |
| `x-ms-throttle-scope` | response | The throttled scope (`<Scope>/<Limit>/<AppId>/<TenantId...>`) |
| `x-ms-throttle-information` | response | Why (`CPULimitExceeded`, `WriteLimitExceeded`, ...) |
| `x-ms-throttle-priority` | request | `low` / `normal` / `high` — low is throttled first |

## What the library does

```python
result = client.users.top(10).get().execute_query_retry()   # honor Retry-After + backoff
client.execute_batch(concurrency=5)                         # retries throttled sub-requests

client.with_rate_limit()          # pace a fleet from the signals (proactive)
client.with_rate_limit(per_scope=True)   # pace each x-ms-throttle-scope separately
client.with_throttle_priority("low")     # mark background work low priority
```

`client.with_rate_limit()` reads every response (including batch sub-responses)
and gates the group on `Retry-After`, Graph's `x-ms-throttle-limit-percentage`
and SharePoint's health score. When a response reports `x-ms-resource-unit`, the
proactive pace is scaled by that request cost, so an expensive call rests
proportionally longer. With `per_scope=True` a throttled `x-ms-throttle-scope`
pauses only requests tagged with the matching `RequestOptions.throttle_scope`.
See `office365.runtime.http.throttling` and `office365.runtime.retry`.

## Best practices to avoid throttling

- **Honor `Retry-After`** — it is the server telling you exactly how long to
  wait; retrying earlier only extends the throttle.
- **Pace proactively** with `with_rate_limit()`; mark interactive calls
  `with_throttle_priority("high")` and background jobs `"low"` so low-priority
  work is throttled first.
- **Share the load**: avoid a large fan-out of concurrent connections; spread
  requests over time rather than bursting.
- **Keep responses small**: use `$select`/`$top`/`$expand` deliberately; avoid
  oversized `$top` and deep expansions that inflate server cost.
- Prefer **delta queries** and **change notifications** over polling/scanning.
- **Batch** related operations (JSON batching) and reduce operations per request.
  Outlook also caps how many requests a mailbox may have **in flight**: four at a
  time, and four sub-requests per JSON batch — so `execute_batch(concurrency=4)` is
  the ceiling a mailbox workload should ask for (`OUTLOOK_QUOTAS` in
  `office365.outlook.quotas`). A higher `concurrency` does not go faster: the
  surplus queues inside the service.
- Watch `X-SharePointHealthScore` — when the farm is busy, ease off before it
  throttles you (the rate limiter already does this).
- Set a descriptive `User-Agent` (e.g. `ISV|Contoso|MyApp/1.0`) so Microsoft can
  attribute and, if needed, raise your limits.
- For bulk extraction, use **Microsoft Graph Data Connect** (not throttled).

## Quotas (reference)

The numbers below are the limits Microsoft publishes; the first one reached triggers
throttling. A **Window** of *in flight* means concurrency rather than a rate. Every row
answers `catalog(product=...)`; the **Bound at** column names the model that declares
it (most rows are referenced by no model, and are reference data only).

"""


def _emit(path: str, content: str) -> None:
    with mkdocs_gen_files.open(path, "w") as f:
        f.write(content)


def _window(row: Limit) -> str:
    if row.window_seconds is None:
        return "—"
    if row.window_seconds == 0:
        return "in flight"
    return f"{row.window_seconds}s"


def _value(row: Limit) -> str:
    unit = row.unit[:-1] if row.value == 1 and row.unit.endswith("s") else row.unit
    return f"{row.value:,} {unit}"


_bindings = scan_bindings(_REPO_ROOT / "office365")
_names = row_attrs()
_products = [name for name in catalog_products() if name not in ("sharepoint", "model")]
_products.sort(key=lambda name: (name != "graph", name))

_rows = [
    "| Product | Limit | Value | Window | Scope | Type | Bound at | Notes |",
    "| --- | --- | --- | --- | --- | --- | --- | --- |",
]
for _product in _products:
    for _row in catalog(product=_product):
        _name = f"[{_row.name}]({_row.doc})" if _row.doc else _row.name
        _rows.append(
            f"| `{_product}` | {_name} | {_value(_row)} | {_window(_row)} | {_row.scope} "
            f"| {_row.request_type or 'any'} | {bound_at(_row, _bindings, _names) or '—'} | {_row.note} |"
        )

_emit("throttling.md", "\n".join([_HEADER, *_rows, ""]))
