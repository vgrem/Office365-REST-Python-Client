"""Microsoft Graph cloud-communications throttling quotas (reference).

Declared on the model with ``@limit(*CALL_QUOTAS)`` etc. (see ``Call``,
``CallRecord``, ``Presence``, ``VirtualEvent``). Reference-only — the library reacts to the
server signals (:mod:`office365.runtime.http.throttling`). The catalog registers
itself at import, so `office365.limits.catalog()` sees these rows.

Source: https://learn.microsoft.com/en-us/graph/throttling-limits
"""

from __future__ import annotations

from office365.runtime.limits import Limit, LimitKind, register_catalog

_DOC = "https://learn.microsoft.com/en-us/graph/throttling-limits"
_SUPPORTED = LimitKind.SUPPORTED

CALL_QUOTAS = (
    Limit(
        "cloud communications",
        50_000,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="calls",
        doc=_DOC,
        window_seconds=15,
    ),
)

PRESENCE_QUOTAS = (
    Limit(
        "cloud communications",
        10_000,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="presence",
        doc=_DOC,
        window_seconds=30,
    ),
)

CALL_RECORD_QUOTAS = (
    Limit("call records", 15_000, _SUPPORTED, "requests", "app", doc=_DOC, window_seconds=20),
    Limit("call records", 10_000, _SUPPORTED, "requests", "tenant", doc=_DOC, window_seconds=20),
    Limit("call records", 1_500, _SUPPORTED, "requests", "app+tenant", doc=_DOC, window_seconds=20),
    Limit(
        "call records",
        40,
        _SUPPORTED,
        "requests",
        "resource",
        note="per call record",
        doc=_DOC,
        window_seconds=20,
    ),
)

VIRTUAL_EVENT_QUOTAS = (
    Limit(
        "cloud communications",
        750,
        _SUPPORTED,
        "requests",
        "app",
        request_type="read",
        note="virtual events",
        doc=_DOC,
        window_seconds=30,
    ),
    Limit(
        "cloud communications",
        15,
        _SUPPORTED,
        "requests",
        "app",
        request_type="write",
        note="virtual events",
        doc=_DOC,
        window_seconds=30,
    ),
)

register_catalog(CALL_QUOTAS, CALL_RECORD_QUOTAS, PRESENCE_QUOTAS, VIRTUAL_EVENT_QUOTAS, product="cloud-communications")
