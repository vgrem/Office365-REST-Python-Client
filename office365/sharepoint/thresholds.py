"""SharePoint service limits — the single source of truth.

Declares the limits the library can act on as :class:`~office365.runtime.limits.Limit`
values (value + kind + unit + scope + docs), and re-exports the guard-rail helpers
(:func:`warn_if_exceeds`, :func:`ensure_within`, :func:`bounded`, ...).

Sources:

- SharePoint in Microsoft 365 limits —
  https://learn.microsoft.com/en-us/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits
- Software boundaries and limits (SharePoint Server 2016/2019) —
  https://learn.microsoft.com/en-us/sharepoint/install/software-boundaries-limits-2019

The list-view threshold (:data:`LIST_VIEW_THRESHOLD`) is the one most callers
hit: SharePoint blocks queries that filter/sort on a non-indexed column and would
scan/return more items than it, and trims some single-shot collection loads to it.
"""

from __future__ import annotations

from office365.runtime.limits import (
    DEFAULT_BATCH_SIZE,
    SAFE_PAGE_SIZE,
    Limit,
    LimitDecl,
    LimitExceededError,
    LimitKind,
    LimitReport,
    bounded,
    catalog,
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
    "LIST_VIEW_THRESHOLD",
    "SAFE_PAGE_SIZE",
    "Limit",
    "LimitDecl",
    "LimitExceededError",
    "LimitKind",
    "LimitReport",
    "Limits",
    "bounded",
    "catalog",
    "ensure_within",
    "exceeds",
    "hint",
    "limit",
    "limits_of",
    "register_catalog",
    "verify_limits",
    "warn_if_exceeds",
]

_DOC_ONLINE = (
    "https://learn.microsoft.com/en-us/office365/servicedescriptions/"
    "sharepoint-online-service-description/sharepoint-online-limits"
)
_DOC_SERVER = "https://learn.microsoft.com/en-us/sharepoint/install/software-boundaries-limits-2019"
_DOC_THROTTLING = (
    "https://learn.microsoft.com/en-us/sharepoint/dev/general-development/"
    "how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online"
)

_KB = 1024
_MB = 1024 * _KB
_GB = 1024 * _MB
_TB = 1024 * _GB

_BOUNDARY = LimitKind.BOUNDARY
_THRESHOLD = LimitKind.THRESHOLD
_SUPPORTED = LimitKind.SUPPORTED


class Limits:
    """SharePoint limits the client can act on, as :class:`Limit` values.

    Each attribute is a :class:`Limit` — ``Limits.LIST_VIEW.value`` is ``5000``,
    ``str(Limits.FILE_UPLOAD)`` is ``"250 GB"``. Iterate with
    :meth:`catalog` to render a reference table.
    """

    # --- Queries and list/folder operations ---------------------------------
    LIST_VIEW = Limit(
        "list view threshold",
        5000,
        _THRESHOLD,
        "items",
        "list",
        "page through the data or index the filtered/sorted column to exceed it",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    LIST_VIEW_ADMIN = Limit(
        "list view threshold (auditors/admins)",
        20000,
        _THRESHOLD,
        "items",
        "list",
        "",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    INDEX_ADD_REMOVE = Limit(
        "index add/remove threshold",
        20000,
        _THRESHOLD,
        "items",
        "list",
        "applies while adding or removing a column index",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    DELETE_ITEMS = Limit(
        "delete list/folder threshold",
        100000,
        _THRESHOLD,
        "items",
        "list",
        "",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    RENAME_FOLDER = Limit(
        "rename folder threshold",
        100000,
        _THRESHOLD,
        "items",
        "folder",
        "renaming a folder within the same library",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    LOOKUP_JOINS = Limit(
        "list view lookup threshold",
        8,
        _THRESHOLD,
        "joins",
        "query",
        "queries with more joins are blocked",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    MAX_LIST_ITEMS = Limit(
        "max items per list/library",
        30_000_000,
        _SUPPORTED,
        "items",
        "list",
        "",
        f"{_DOC_ONLINE}#items-in-lists-and-libraries",
    )

    # --- Columns ------------------------------------------------------------
    MAX_INDEXED_COLUMNS = Limit(
        "max indexed columns",
        20,
        _SUPPORTED,
        "columns",
        "list",
        "SharePoint Online allows roughly 20 indexed columns",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    TEXT_COLUMN = Limit(
        "single line of text column length",
        255,
        _THRESHOLD,
        "chars",
        "column",
        "indexed text columns are limited to 255 characters",
        f"{_DOC_SERVER}#column-limits",
    )
    LIST_ROW_BYTES = Limit(
        "list row size",
        8000,
        _BOUNDARY,
        "bytes",
        "list item",
        "300 bytes are reserved; ~7,700 are usable",
        f"{_DOC_SERVER}#column-limits",
    )

    # --- Files: upload, download, paths -------------------------------------
    FILE_UPLOAD = Limit(
        "file upload",
        250 * _GB,
        _BOUNDARY,
        "bytes",
        "file",
        "SharePoint Server 2016/2019 caps at 10 GB (15 GB in Subscription Edition)",
        f"{_DOC_ONLINE}#file-size-and-file-path-length",
    )
    LIST_ITEM_ATTACHMENT = Limit(
        "file attached to a list item",
        250 * _MB,
        _BOUNDARY,
        "bytes",
        "list item",
        "",
        f"{_DOC_ONLINE}#file-size-and-file-path-length",
    )
    ZIP_DOWNLOAD = Limit(
        "ZIP download",
        20 * _GB,
        _BOUNDARY,
        "bytes",
        "download",
        "the autogenerated ZIP when downloading multiple files",
        f"{_DOC_ONLINE}#file-size-and-file-path-length",
    )
    UPLOAD_SIMPLE = Limit(
        "simple upload (Files/add)",
        4 * _MB,
        _THRESHOLD,
        "bytes",
        "file",
        "larger files use a resumable upload session",
        f"{_DOC_ONLINE}#file-size-and-file-path-length",
    )
    UPLOAD_SESSION_CHUNK = Limit(
        "upload session chunk",
        4 * _MB,
        _SUPPORTED,
        "bytes",
        "file",
        "default chunk size for resumable uploads",
        f"{_DOC_ONLINE}#file-size-and-file-path-length",
    )
    FILE_PATH_LENGTH = Limit(
        "decoded file path length",
        400,
        _BOUNDARY,
        "chars",
        "file",
        "the folder path plus file name after decoding",
        f"{_DOC_ONLINE}#file-size-and-file-path-length",
    )
    LONG_ONEDRIVE_URL = Limit(
        "long OneDrive URL",
        400,
        _BOUNDARY,
        "chars",
        "url",
        "the decoded full file URL; OneDrive/SharePoint sync fails beyond it",
        f"{_DOC_ONLINE}#file-size-and-file-path-length",
    )
    FILE_NAME_LENGTH = Limit(
        "file name length",
        128,
        _THRESHOLD,
        "chars",
        "file",
        "the FileLeafRef name; the migration path scanner flags longer names",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    LARGE_EXCEL_FILE = Limit(
        "Excel workbook opened in the browser",
        10 * _MB,
        _THRESHOLD,
        "bytes",
        "file",
        "larger Excel files prompt to open in the Excel client instead of the browser",
        _DOC_ONLINE,
    )

    # --- Batching -----------------------------------------------------------
    BATCH_ITEMS = Limit(
        "items per bulk/batch operation",
        DEFAULT_BATCH_SIZE,
        _BOUNDARY,
        "items",
        "batch",
        "the OData batch size the client uses",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    BATCH_BYTES = Limit(
        "batch request size",
        1 * _MB,
        _SUPPORTED,
        "bytes",
        "batch",
        "conservative client cap for a SharePoint OData batch",
        f"{_DOC_THROTTLING}#how-to-handle-throttling",
    )

    # --- Managed metadata ---------------------------------------------------
    MANAGED_TERMS = Limit(
        "managed metadata terms",
        1_000_000,
        _SUPPORTED,
        "terms",
        "tenant",
        "global and site-level terms combined",
        f"{_DOC_ONLINE}#managed-metadata",
    )
    MANAGED_TERM_LABELS = Limit(
        "managed metadata term labels",
        2_000_000,
        _SUPPORTED,
        "labels",
        "tenant",
        "",
        f"{_DOC_ONLINE}#managed-metadata",
    )
    MANAGED_TERM_PROPERTIES = Limit(
        "managed metadata term properties",
        1_000_000,
        _SUPPORTED,
        "properties",
        "tenant",
        "",
        f"{_DOC_ONLINE}#managed-metadata",
    )
    TERM_SETS = Limit(
        "global term sets",
        1000,
        _SUPPORTED,
        "term sets",
        "tenant",
        "",
        f"{_DOC_ONLINE}#managed-metadata",
    )
    TERM_GROUPS = Limit(
        "global term groups",
        1000,
        _SUPPORTED,
        "term groups",
        "tenant",
        "",
        f"{_DOC_ONLINE}#managed-metadata",
    )
    DEFAULT_TERMS = Limit(
        "terms per managed metadata column (default)",
        50,
        _SUPPORTED,
        "terms",
        "column",
        "more than this is allowed but downstream experiences aren't guaranteed",
        f"{_DOC_ONLINE}#managed-metadata",
    )

    # --- Security -----------------------------------------------------------
    PERMISSION_INHERITANCE = Limit(
        "permission inheritance break/reinherit",
        100_000,
        _THRESHOLD,
        "items",
        "list",
        "above this many items you can't break or reinherit permissions on the list/folder",
        f"{_DOC_ONLINE}#items-in-lists-and-libraries",
    )
    UNIQUE_SCOPES = Limit(
        "unique security scopes",
        50_000,
        _THRESHOLD,
        "scopes",
        "list",
        "the recommended general limit is 5,000",
        f"{_DOC_ONLINE}#unique-security-scopes-per-list-or-library",
    )
    UNIQUE_SCOPES_RECOMMENDED = Limit(
        "recommended unique security scopes",
        5000,
        _SUPPORTED,
        "scopes",
        "list",
        "",
        f"{_DOC_ONLINE}#unique-security-scopes-per-list-or-library",
    )
    ACL_PROPAGATION = Limit(
        "ACL propagation child objects",
        500,
        _THRESHOLD,
        "objects",
        "list",
        "propagation fails beyond this many uniquely scoped children",
        f"{_DOC_SERVER}#list-and-library-limits",
    )
    GROUPS_PER_SITE = Limit(
        "SharePoint groups per site",
        10_000,
        _SUPPORTED,
        "groups",
        "site",
        "",
        f"{_DOC_ONLINE}#sharepoint-groups",
    )
    GROUP_MEMBERS = Limit(
        "users per SharePoint group",
        5000,
        _SUPPORTED,
        "users",
        "group",
        "",
        f"{_DOC_ONLINE}#sharepoint-groups",
    )
    COMPLIANCE_POLICIES = Limit(
        "compliance policies per tenant",
        10_000,
        _SUPPORTED,
        "policies",
        "tenant",
        "eDiscovery/retention holds count toward this, shared with DLP and sensitivity labels",
        f"{_DOC_ONLINE}#hold-limits",
    )

    # --- Versions -----------------------------------------------------------
    MAJOR_VERSIONS = Limit(
        "major versions",
        50_000,
        _SUPPORTED,
        "versions",
        "file",
        "SharePoint Server 2019 allows 400,000",
        f"{_DOC_ONLINE}#versions",
    )
    MINOR_VERSIONS = Limit(
        "minor versions",
        511,
        _BOUNDARY,
        "versions",
        "file",
        "",
        f"{_DOC_ONLINE}#versions",
    )

    # --- Site structure and storage -----------------------------------------
    LISTS_PER_SITE = Limit(
        "lists and libraries per site collection",
        2000,
        _SUPPORTED,
        "lists",
        "site",
        "",
        f"{_DOC_ONLINE}#lists-and-libraries",
    )
    SUBSITES_PER_SITE = Limit(
        "subsites per site",
        2000,
        _THRESHOLD,
        "sites",
        "site",
        "",
        f"{_DOC_ONLINE}#subsites",
    )
    SITE_STORAGE = Limit(
        "max storage per site collection",
        25 * _TB,
        _BOUNDARY,
        "bytes",
        "site",
        "",
        f"{_DOC_ONLINE}#limits-by-plan",
    )
    SITE_METADATA = Limit(
        "overall site metadata",
        1000 * _GB,
        _SUPPORTED,
        "bytes",
        "site",
        "metadata rarely reaches this size",
        f"{_DOC_ONLINE}#overall-site-metadata",
    )

    # --- Move/copy and sync -------------------------------------------------
    MOVE_COPY_BYTES = Limit(
        "move/copy total file size",
        100 * _GB,
        _THRESHOLD,
        "bytes",
        "transfer",
        "across sites and containers",
        f"{_DOC_ONLINE}#moving-and-copying-across-sites-and-containers",
    )
    MOVE_COPY_FILES = Limit(
        "move/copy file count",
        30_000,
        _THRESHOLD,
        "files",
        "transfer",
        "",
        f"{_DOC_ONLINE}#moving-and-copying-across-sites-and-containers",
    )
    CROSS_GEO_FILE = Limit(
        "cross-geo copy/move file size",
        15 * _GB,
        _THRESHOLD,
        "bytes",
        "file",
        "",
        f"{_DOC_ONLINE}#moving-and-copying-across-sites-and-containers",
    )
    ONENOTE_FILE = Limit(
        "OneNote file in move/copy",
        2 * _GB,
        _THRESHOLD,
        "bytes",
        "file",
        "",
        f"{_DOC_ONLINE}#moving-and-copying-across-sites-and-containers",
    )
    MIGRATION_FILE_SIZE = Limit(
        "large file for migration (SMAT)",
        15 * _GB,
        _SUPPORTED,
        "bytes",
        "file",
        "SMAT flags files over this as slow/hard to migrate; SPO upload allows 250 GB (SP2019 10-15 GB)",
        f"{_DOC_ONLINE}#file-size-and-file-path-length",
    )
    SYNC_FILES = Limit(
        "files in a synced library",
        300_000,
        _SUPPORTED,
        "files",
        "library",
        "OneDrive sync performance limit",
        f"{_DOC_ONLINE}#sync",
    )

    @classmethod
    def catalog(cls) -> list[Limit]:
        """Every declared limit, ordered by definition."""
        return [value for value in vars(cls).values() if isinstance(value, Limit)]


# The list-view threshold is the one callers reference most often; keep a module
# constant for backward compatibility and ergonomics.
LIST_VIEW_THRESHOLD = Limits.LIST_VIEW.value

# Register this product's vocabulary with the limits registry (``office365.limits``).
register_catalog(Limits, product="sharepoint")
