"""Generate the service-limits reference page (mkdocs-gen-files plugin).

The table mirrors :meth:`office365.sharepoint.thresholds.Limits.catalog`, so the docs
can't drift from the code, and adds a **Bound at** column scanned from the ``@limit``
decorators on the model. The Graph throttling quotas — the other half of the same
``Limit`` vocabulary — are tabulated in [Throttling](throttling.md), because there they
have to be read next to the signals that make them dynamic. mkdocs-gen-files executes
this module with ``runpy``, so emission happens at module level.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import mkdocs_gen_files  # noqa: E402
from _limit_bindings import bound_at, row_attrs, scan_bindings  # noqa: E402
from office365.sharepoint.thresholds import Limits  # noqa: E402

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

_HEADER = """# Service limits

SharePoint enforces the limits below. The library declares them in
`office365.sharepoint.thresholds.Limits` and binds the ones a call can be measured
against to the model with the `@limit` decorator — **warnings by default**, never a
silent truncation. The list view threshold is the one most callers meet; see
[Large lists and folders](large-lists.md) for the paging and indexing recipes.

The other kind of row in the same vocabulary is a **throttling quota** — a rate Graph
allows per app, tenant, mailbox or resource. Those are **reference only**: the library
reacts to the server signals (`Retry-After`, `x-ms-throttle-*`, `RateLimit-*`,
`X-SharePointHealthScore`) rather than simulating the token bucket. They are tabulated
with the signals in [Throttling](throttling.md), and every row is answerable as data:

```python
from office365.limits import catalog, catalog_products
from office365.sharepoint.thresholds import Limits, limit, warn_if_exceeds

warn_if_exceeds(Limits.LIST_VIEW, item_count, context="list 'Orders'")

@limit(Limits.LIST_VIEW, arg="page_size")   # declare + enforce on the model
def get_items(page_size=None): ...

catalog_products()  # ['graph', 'directory', 'outlook', 'teams', 'sharepoint', ...]
catalog("sharepoint")  # the table below, as data
```

Sources:

- [SharePoint in Microsoft 365 limits](https://learn.microsoft.com/en-us/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits)
- [Software boundaries and limits (SharePoint Server 2016/2019)](https://learn.microsoft.com/en-us/sharepoint/install/software-boundaries-limits-2019)
- [Microsoft Graph throttling limits](https://learn.microsoft.com/en-us/graph/throttling-limits)
"""

_ASSESSMENT = """## Migration assessment

The pre-migration assessment (`MigrationAssessor` / `MigrationTenantAssessor`)
reports several of these limits as [SPMT scan-assessment risk codes](https://learn.microsoft.com/en-us/sharepointmigration/spmt-scan-risk-codes):

| SPMT risk code | Limit | Scanner |
| --- | --- | --- |
| `LIST_VIEW_EXCEED_LIMIT` | list view threshold | `LargeListScanner` |
| `ITEM_COUNT_EXCEED_INDEX_LIMIT` | index add/remove threshold | `LargeListScanner` |
| `ITEM_COUNT_EXCEED_LIMIT` | max items per list/library | `LargeListScanner` |
| `LIST_VIEW_LOOKUP_EXCEED_LIMIT` | list view lookup threshold | `LookupColumnScanner` |
| `UNIQUE_PERMISSION_EXCEED_LIMIT` | unique security scopes | `PermissionScanner` |

Each `AssessmentIssue` carries the `risk_code`, and `report.by_risk_code` groups
the issues by code. The `LongOneDriveUrls` detail report (`LongOneDriveUrlsScanner`)
additionally flags files whose full URL crosses `LONG_ONEDRIVE_URL`; `ThicketFolder`
(`THICKET_FOLDER_UNSUPPORTED`) and `UnsupportedSiteTemplates` cover the remaining
blockers.
"""


def _emit(path: str, content: str) -> None:
    with mkdocs_gen_files.open(path, "w") as f:
        f.write(content)


_bindings = scan_bindings(_REPO_ROOT / "office365")
_names = row_attrs()

_rows = [
    "| Limit | Value | Kind | Scope | Bound at | Notes |",
    "| --- | --- | --- | --- | --- | --- |",
]
for _row in Limits.catalog():
    _name = f"[{_row.name}]({_row.doc})" if _row.doc else _row.name
    _rows.append(
        f"| {_name} | {_row} | {_row.kind.value} | {_row.scope} "
        f"| {bound_at(_row, _bindings, _names) or '—'} | {_row.note} |"
    )

_emit("limits.md", "\n".join([_HEADER, *_rows, "", _ASSESSMENT]))
