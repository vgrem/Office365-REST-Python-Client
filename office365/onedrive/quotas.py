"""OneDrive and SharePoint "Files and lists" throttling quotas (reference).

Graph's own *Files and lists* section defers to the SharePoint Online throttling
document, because both surfaces are the same service and the same resource-unit
budget. Every request costs resource units: **1** for a single-item query, a delta
with a token, or a file download; **2** for a multi-item query (list children) or a
create/update/delete/upload; **5** for any permission operation (``$expand=permissions``
included). The rate limits are therefore budgets, not request counts — divide by the
average cost to estimate a request rate.

Reference-only: the library reacts to the server signals
(:mod:`office365.runtime.http.throttling` — ``RateLimit-*``, ``Retry-After``,
``X-SharePointHealthScore``) and retries with backoff. It does not model the bucket.

Source: https://learn.microsoft.com/en-us/sharepoint/dev/general-development/how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online
"""

from __future__ import annotations

from office365.runtime.limits import Limit, LimitKind, register_catalog

_DOC = (
    "https://learn.microsoft.com/en-us/sharepoint/dev/general-development/"
    "how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online"
)
_THRESHOLD = LimitKind.THRESHOLD

FILES_QUOTAS = (
    # --- per user -------------------------------------------------------------
    Limit("files and lists", 3_000, _THRESHOLD, "requests", "user", doc=_DOC, window_seconds=300),
    Limit(
        "files and lists",
        50 * 1024**3,
        _THRESHOLD,
        "bytes",
        "user",
        note="ingress",
        doc=_DOC,
        window_seconds=3_600,
    ),
    Limit(
        "files and lists",
        100 * 1024**3,
        _THRESHOLD,
        "bytes",
        "user",
        note="egress",
        doc=_DOC,
        window_seconds=3_600,
    ),
    # --- per app per tenant ---------------------------------------------------
    Limit(
        "files and lists",
        1_250,
        _THRESHOLD,
        "resource_units",
        "app+tenant",
        note="tiers by license count: 1,250 (<1,000 users); 2,500 (<5,000); "
        "3,750 (<15,000); 5,000 (<50,000); 6,250 (50,000+)",
        doc=_DOC,
        window_seconds=60,
    ),
    Limit(
        "files and lists",
        300,
        _THRESHOLD,
        "requests",
        "app+tenant",
        note="specific sharing APIs",
        doc=_DOC,
        window_seconds=300,
    ),
    Limit(
        "files and lists",
        400 * 1024**3,
        _THRESHOLD,
        "bytes",
        "app+tenant",
        note="ingress",
        doc=_DOC,
        window_seconds=3_600,
    ),
    Limit(
        "files and lists",
        400 * 1024**3,
        _THRESHOLD,
        "bytes",
        "app+tenant",
        note="egress",
        doc=_DOC,
        window_seconds=3_600,
    ),
    # --- per site -------------------------------------------------------------
    Limit(
        "files and lists",
        3_000,
        _THRESHOLD,
        "requests",
        "site",
        note="anonymous links",
        doc=_DOC,
        window_seconds=300,
    ),
    Limit(
        "files and lists",
        100 * 1024**3,
        _THRESHOLD,
        "bytes",
        "site",
        note="anonymous egress (download)",
        doc=_DOC,
        window_seconds=7_200,
    ),
)

register_catalog(FILES_QUOTAS, product="files")
