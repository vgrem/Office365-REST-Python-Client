"""Unified access to service limits — mechanics, catalogs and discovery.

The library declares limits in three layers:

- **Mechanics** (:mod:`office365.runtime.limits`): :class:`Limit` (a static
  threshold *or* a rate quota), the :func:`limit` decorator, and the guardrails
  (:func:`exceeds` / :func:`warn_if_exceeds` / :func:`ensure_within` /
  :func:`hint`).
- **Catalogs**: product vocabularies — ``sharepoint.thresholds.Limits`` (SharePoint
  and CSOM thresholds) and one ``quotas`` module per Graph product (``outlook``,
  ``teams``, ``reports``, ``security``, ``onedrive``, ``onedrive.workbooks``,
  ``directory``, ``communications``), plus the single Graph-wide row in
  :mod:`office365.runtime.limits`. A catalog is data: it registers itself at import,
  and importing this module imports all of them.
- **Discovery**: a class carries its limits via ``@limit`` (``declared_limits()``);
  :func:`limits_of` / :func:`verify_limits` inspect them; :func:`catalog`
  aggregates every registered source and :func:`catalog_products` lists the keys
  it takes.

Products register their catalogs with :func:`register_catalog`; ``@limit`` on a
class registers that class automatically (under ``product="model"``).
"""

from __future__ import annotations

# Product catalogs register themselves when imported, so import every one of them here:
# ``catalog()`` must answer for all products, not only for the ones the caller happened
# to touch first. Each module is a few rows of literals: the whole set costs ~3 ms.
import office365.communications.quotas  # noqa: F401
import office365.directory.quotas  # noqa: F401
import office365.onedrive.quotas  # noqa: F401
import office365.onedrive.workbooks.quotas  # noqa: F401
import office365.outlook.quotas  # noqa: F401
import office365.reports.quotas  # noqa: F401
import office365.security.quotas  # noqa: F401
import office365.sharepoint.thresholds  # noqa: F401
import office365.teams.quotas  # noqa: F401
from office365.runtime.limits import (
    DEFAULT_BATCH_SIZE,
    SAFE_PAGE_SIZE,
    Limit,
    LimitCatalog,
    LimitDecl,
    LimitExceededError,
    LimitKind,
    LimitReport,
    bounded,
    catalog,
    catalog_products,
    collect_class_limits,
    collect_limit_meta,
    ensure_within,
    exceeds,
    hint,
    limit,
    limits_of,
    register_catalog,
    verify_limits,
    warn_if_exceeds,
)

__all__ = [
    "DEFAULT_BATCH_SIZE",
    "SAFE_PAGE_SIZE",
    "Limit",
    "LimitCatalog",
    "LimitDecl",
    "LimitExceededError",
    "LimitKind",
    "LimitReport",
    "bounded",
    "catalog",
    "catalog_products",
    "collect_class_limits",
    "collect_limit_meta",
    "ensure_within",
    "exceeds",
    "hint",
    "limit",
    "limits_of",
    "register_catalog",
    "verify_limits",
    "warn_if_exceeds",
]
