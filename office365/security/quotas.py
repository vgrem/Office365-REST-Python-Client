"""Security throttling quotas (reference).

Three surfaces, three budgets, none of which is a request-rate bucket in the usual
sense:

* ``/security/alerts``, ``securityActions``, ``secureScore`` and ``tiIndicator`` are
  throttled per app per tenant, with ``secureScore`` additionally capped on concurrent
  requests.
* ``/security/eDiscoveryCases`` is minute-rate limited.
* The Purview audit log query API (``/security/auditLog/queries``) is capped at the
  **tenant** level on a rolling 24-hour window, so its limits read as per-day
  allocations rather than rates. Its per-query record cap is not an error: the query
  still succeeds and reports ``isRecordCountLimitExceeded``, which is why
  :class:`office365.security.audit.log_query.AuditLogQuery` surfaces that property
  instead of raising.

Reference-only: the library reacts to the server signals
(:mod:`office365.runtime.http.throttling`).

Source: https://learn.microsoft.com/en-us/graph/throttling-limits#security-detections-and-incidents-service-limits
"""

from __future__ import annotations

from office365.runtime.limits import Limit, LimitKind, register_catalog

_BASE = "https://learn.microsoft.com/en-us/graph/throttling-limits"
_DOC = f"{_BASE}#security-detections-and-incidents-service-limits"
_DOC_AUDIT = f"{_BASE}#security-audit-log-query-service-limits"
_DOC_EDISCOVERY = f"{_BASE}#security-ediscovery-service-limits"
_SUPPORTED = LimitKind.SUPPORTED
_THRESHOLD = LimitKind.THRESHOLD

SECURITY_QUOTAS = (
    # --- detections and incidents --------------------------------------------
    Limit(
        "security",
        150,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="alert, securityActions, secureScore",
        doc=_DOC,
        window_seconds=60,
    ),
    Limit(
        "security",
        1_000,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="tiIndicator",
        doc=_DOC,
        window_seconds=60,
    ),
    Limit(
        "security",
        10_000,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="secureScore, secureScorecontrolProfile",
        doc=_DOC,
        window_seconds=600,
    ),
    Limit(
        "security",
        4,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="secureScore, secureScorecontrolProfile — in flight at any moment",
        doc=_DOC,
        window_seconds=0,
    ),
    # --- eDiscovery -----------------------------------------------------------
    Limit(
        "security",
        5,
        _SUPPORTED,
        "requests",
        "app+tenant",
        note="eDiscovery cases",
        doc=_DOC_EDISCOVERY,
        window_seconds=60,
    ),
    # --- Purview audit log query ---------------------------------------------
    Limit(
        "security",
        200,
        _THRESHOLD,
        "requests",
        "tenant",
        note="audit log query submissions per rolling 24 hours; baseline, may be higher",
        doc=_DOC_AUDIT,
        window_seconds=86_400,
    ),
    Limit(
        "security",
        50,
        _THRESHOLD,
        "requests",
        "tenant",
        note="audit log queries queued or running at any moment",
        doc=_DOC_AUDIT,
        window_seconds=0,
    ),
    Limit(
        "security",
        1_000_000,
        _THRESHOLD,
        "records",
        "query",
        note="per audit log query; exceeding it ends the query successfully, with isRecordCountLimitExceeded set",
        doc=_DOC_AUDIT,
    ),
)

register_catalog(SECURITY_QUOTAS, product="security")
