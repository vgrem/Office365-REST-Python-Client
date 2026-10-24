"""Microsoft Graph identity throttling quotas (reference).

Declared on the model with ``@limit(*IDENTITY_QUOTAS)`` (see ``DirectoryObject``,
``SubscribedSku``, ``Domain``) — Graph throttles the identity API surface with a
**ResourceUnits** token bucket plus write quotas. Reference-only: the library
reacts to the server signals (:mod:`office365.runtime.http.throttling`). The catalog
registers itself at import, so `office365.limits.catalog()` sees these rows.

Source: https://learn.microsoft.com/en-us/graph/throttling-limits
"""

from __future__ import annotations

from office365.runtime.limits import Limit, LimitKind, register_catalog

_DOC = "https://learn.microsoft.com/en-us/graph/throttling-limits"
_SUPPORTED = LimitKind.SUPPORTED

#: Identity and access quotas (the whole `/users`, `/groups`, ... surface).
IDENTITY_QUOTAS = (
    Limit(
        "identity",
        3_500,
        _SUPPORTED,
        "resource_units",
        "app+tenant",
        note="small tenants (<50 users); 5,000 medium (50-500), 8,000 large (>500)",
        doc=_DOC,
        window_seconds=10,
    ),
    Limit("identity", 150_000, _SUPPORTED, "resource_units", "app", doc=_DOC, window_seconds=20),
    Limit("identity", 3_000, _SUPPORTED, "requests", "app+tenant", doc=_DOC, window_seconds=150, request_type="write"),
    Limit("identity", 35_000, _SUPPORTED, "requests", "app", doc=_DOC, window_seconds=300, request_type="write"),
    Limit("identity", 18_000, _SUPPORTED, "requests", "tenant", doc=_DOC, window_seconds=300, request_type="write"),
)

register_catalog(IDENTITY_QUOTAS, product="directory")
