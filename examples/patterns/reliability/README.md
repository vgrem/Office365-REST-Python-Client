# Reliability

What to do when the service pushes back: read structured errors, honor
throttling, and retry the right way.

| Example | Shows |
|---|---|
| [`errors.py`](./errors.py) | The `ClientRequestException` shape (`code`, `message`, `inner_error`) and how to branch on 401/403/404/429 |

Related:

- retry with backoff — [`../async/retry_async.py`](../async/retry_async.py)
- rate-limited bulk work — [`../async/rate_limited_bulk_create.py`](../async/rate_limited_bulk_create.py)
- the LRO poller already honors `Retry-After` — [`../lro/`](../lro/)

https://learn.microsoft.com/en-us/graph/errors
https://learn.microsoft.com/en-us/graph/throttling
