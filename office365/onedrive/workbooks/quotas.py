"""Excel (workbooks) throttling quotas (reference).

The workbooks API is throttled separately from the rest of the Files surface, per app
across all tenants and per app per tenant. Excel is *also* subject to the SharePoint
resource-unit budget (:mod:`office365.onedrive.quotas`) — a workbook call is a files
call — so the two catalogs stack; whichever the service checks first wins.

Reference-only: the library reacts to the server signals
(:mod:`office365.runtime.http.throttling`).

Source: https://learn.microsoft.com/en-us/graph/throttling-limits#excel-service-limits
"""

from __future__ import annotations

from office365.runtime.limits import Limit, LimitKind, register_catalog

_DOC = "https://learn.microsoft.com/en-us/graph/throttling-limits#excel-service-limits"
_SUPPORTED = LimitKind.SUPPORTED

EXCEL_QUOTAS = (
    Limit(
        "excel",
        5_000,
        _SUPPORTED,
        "requests",
        "app",
        note="all tenants",
        doc=_DOC,
        window_seconds=10,
    ),
    Limit("excel", 1_500, _SUPPORTED, "requests", "app+tenant", doc=_DOC, window_seconds=10),
)

register_catalog(EXCEL_QUOTAS, product="excel")
