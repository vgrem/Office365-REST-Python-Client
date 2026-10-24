"""Microsoft Teams throttling quotas (reference).

Teams evaluates four independent dimensions — **per app** (one client id across every
tenant), **per app per tenant**, **per resource** (a single team, channel or chat) and
**per user** — and a request is throttled by the first one it reaches. Rates are
requests per second, and each is a short burst window; a sustained workload is also
judged against a longer window at roughly 83% of the listed rate, so steady-state
traffic should sit below the number, not at it.

The rows below are the defaults, which cover any request a resource-specific table
does not name (`GET /teams/{id}`, `GET .../channels`, channel messages and chats are
called out because they are what this library is used for). A dash in the published
table means no dedicated limit for that dimension — the row is simply absent here.

Reference-only: the library reacts to the server signals
(:mod:`office365.runtime.http.throttling`) and retries with backoff.

Source: https://learn.microsoft.com/en-us/graph/throttling-limits#microsoft-teams-service-limits
"""

from __future__ import annotations

from office365.runtime.limits import Limit, LimitKind, register_catalog

_DOC = "https://learn.microsoft.com/en-us/graph/throttling-limits#microsoft-teams-service-limits"
_SUPPORTED = LimitKind.SUPPORTED

#: The published table's four columns, in order.
_SCOPES = ("app", "app+tenant", "team, channel or chat", "user")

#: Default row per request type: (request_type, per-app, per-app-per-tenant, per-resource, per-user).
_DEFAULT_ROWS = (
    ("read", 1_500, 30, 1, 1),
    ("write", 300, 30, 1, 1),
    ("delete", 150, 15, 1, 1),
)

_DEFAULTS = tuple(
    Limit(
        "microsoft teams",
        value,
        _SUPPORTED,
        "requests",
        scope,
        note="default — any request a resource table does not name",
        doc=_DOC,
        window_seconds=1,
        request_type=request_type,
    )
    for request_type, *values in _DEFAULT_ROWS
    for scope, value in zip(_SCOPES, values)
)

_RESOURCES = (
    # (operation, dimension, rps) — only the dimensions the published table fills in.
    ("GET /teams/{id}", "app", 1_500),
    ("GET /teams/{id}", "app+tenant", 30),
    ("GET /teams/{id}", "team, channel or chat", 4),
    ("GET /teams/{id}/channels", "app", 1_200),
    ("GET /teams/{id}/channels", "app+tenant", 60),
    ("GET /teams/{id}/channels", "team, channel or chat", 4),
    ("POST /teams/{id}/channels/{id}/messages", "app", 500),
    ("POST /teams/{id}/channels/{id}/messages", "app+tenant", 50),
    ("POST /teams/{id}/channels/{id}/messages", "team, channel or chat", 1),
    ("POST /teams/{id}/channels/{id}/messages", "user", 1),
    ("GET /teams/{id}/channels/{id}/messages", "app", 200),
    ("GET /teams/{id}/channels/{id}/messages", "app+tenant", 20),
    ("GET /teams/{id}/channels/{id}/messages", "team, channel or chat", 1),
    ("GET /chats/{id}/messages", "app", 200),
    ("GET /chats/{id}/messages", "app+tenant", 20),
    ("GET /chats/{id}/messages", "team, channel or chat", 1),
    ("POST /chats/{id}/messages", "app", 200),
    ("POST /chats/{id}/messages", "app+tenant", 20),
    ("POST /chats/{id}/messages", "team, channel or chat", 1),
    ("POST /chats/{id}/messages", "user", 1),
)

TEAMS_QUOTAS = _DEFAULTS + tuple(
    Limit(
        "microsoft teams",
        rate,
        _SUPPORTED,
        "requests",
        scope,
        note=operation,
        doc=_DOC,
        window_seconds=1,
        request_type="read" if operation.startswith("GET") else "write",
    )
    for operation, scope, rate in _RESOURCES
)

register_catalog(TEAMS_QUOTAS, product="teams")
