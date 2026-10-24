"""Microsoft 365 usage-report throttling quotas (reference).

Limit per **app per tenant** and per **tenant for all apps**, counted per report API —
a Teams activity request and an Outlook activity request in the same ten minutes are
one request each out of 14, not two out of the same 14. So a report collector that
walks every report shares one budget per report, not one budget overall.

The CSV rows are what :meth:`office365.reports.report_result.ReportResult.csv_rows`
parses — the default rendition; the JSON row is the beta
``$format=application/json`` preview, which has no tenant-wide counterpart.

Reference-only: the library reacts to the server signals
(:mod:`office365.runtime.http.throttling`).

Source: https://learn.microsoft.com/en-us/graph/throttling-limits#microsoft-365-reports-service-limits
"""

from __future__ import annotations

from office365.runtime.limits import Limit, LimitKind, register_catalog

_DOC = "https://learn.microsoft.com/en-us/graph/throttling-limits#microsoft-365-reports-service-limits"
_SUPPORTED = LimitKind.SUPPORTED

REPORT_QUOTAS = (
    Limit(
        "microsoft 365 reports",
        14,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="CSV, per report API",
        doc=_DOC,
        window_seconds=600,
    ),
    Limit(
        "microsoft 365 reports",
        40,
        _SUPPORTED,
        "requests",
        "tenant",
        note="CSV, per report API, all apps",
        doc=_DOC,
        window_seconds=600,
    ),
    Limit(
        "microsoft 365 reports",
        100,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="JSON (beta), per report API",
        doc=_DOC,
        window_seconds=600,
    ),
)

register_catalog(REPORT_QUOTAS, product="reports")
