"""SharePoint list source/target adapters (REST v1, via the records pipeline).

Migrates list items as records: the source projects loaded items with
``to_records``-style dictionaries and the target imports them with
``from_records`` (deferred, committed in batches). File/folder migrations use
the filesystem/upload adapters.

Lazy imports keep the migration core client-agnostic.
"""

from __future__ import annotations

import hashlib
import io
import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, cast

from typing_extensions import TypeAlias

from office365.migration.adapters import MigrationProgress
from office365.migration.base import (
    MigrationItem,
    PermissionEntry,
    Principal,
    conflict_to_on_conflict,
    normalize_puid,
)
from office365.migration.sharepoint.structure import normalize_guid
from office365.migration.sharepoint.transfer import Failure
from office365.runtime.converters.records import records_from_items
from office365.runtime.converters.scalars import iso_or_none, parse_datetime, parse_int
from office365.runtime.limits import DEFAULT_BATCH_SIZE
from office365.runtime.operations import emit_progress
from office365.sharepoint.fields.builtin_field_name import SYSTEM_FIELD_NAMES
from office365.sharepoint.fields.user_value import FieldUserValue
from office365.sharepoint.principal.type import PrincipalType

if TYPE_CHECKING:
    from office365.migration.map import ContentTypeMap
    from office365.sharepoint.files.file import File
    from office365.sharepoint.folders.folder import Folder
    from office365.sharepoint.lists.list import List as SPList
    from office365.sharepoint.permissions.roles.definitions.definition import RoleDefinition

_TAXONOMY_FIELD_TYPES = {"TaxonomyFieldType", "TaxonomyFieldTypeMulti"}


def _cloned_context(obj):
    """A fresh ``ClientContext`` clone for ``obj`` (same auth + transport, own queue)."""
    ctx = obj.context
    return ctx.clone(ctx.base_url)


def _cloned_list(sp_list: "SPList", context=None) -> "SPList":
    """The same list, addressed by id and loaded on ``context`` (or a clone of it)."""
    list_id = sp_list.id
    if not list_id:
        raise ValueError("cannot rebind a list that was never loaded")
    ctx = context if context is not None else _cloned_context(sp_list)
    return ctx.web.lists.get_by_id(list_id).get().execute_query()


def _cloned_folder(folder: "Folder", context=None) -> "Folder":
    """The same folder, addressed by server-relative path and loaded on ``context``."""
    server_relative_url = folder.server_relative_url
    if not server_relative_url:
        raise ValueError("cannot rebind a folder that was never loaded")
    ctx = context if context is not None else _cloned_context(folder)
    return ctx.web.get_folder_by_server_relative_path(server_relative_url).get().execute_query()


#: The target's typed columns: ``(lookup: name -> referenced list id, user names,
#: multi-lookup: name -> referenced list id, multi-user names, taxonomy:
#: name -> (allows many, hidden note field internal name), multi-choice names)``.
_TypedColumns: TypeAlias = (
    "tuple[dict[str, str], set[str], dict[str, str], set[str], dict[str, tuple[bool, str | None]], set[str]]"
)

# Always-projected system metadata (reliable author/editor identity).
_METADATA_SELECT = ["AuthorId", "EditorId", "HasUniqueRoleAssignments"]
#: Projected system metadata that is read-only and must not be written back.
_NON_WRITABLE_SELECT = frozenset({"HasUniqueRoleAssignments"})

#: Navigation properties a ``*`` read returns that carry no scalar content and can
#: never be written back; they are dropped silently. A genuine typed value we
#: cannot remap (a lookup/person column) is still surfaced as a warning.
_NAVIGATION_SELECT = frozenset(
    {
        "ParentList",
        "ContentType",
        "Folder",
        "File",
        "FieldValuesAsHtml",
        "FieldValuesAsText",
        "FieldValuesForEdit",
    }
)

#: Marker column added to a migrated list recording each item's source id. It makes
#: a re-run idempotent and lets post-run verification pair source and target items.
DEFAULT_LIST_IDENTITY_FIELD = "MigrationSourceId"
# Authorship has its own fidelity path (``apply_authorship``); the built-in Author/
# Editor companion columns are neither content nor Person values to remap.
_PERSON_EXCLUDED = frozenset({"Author", "Editor"})

#: Content-approval state: record key (OData escaped form) -> ``ValidateUpdateListItem``
#: field name. It is ordinary record content, but a *system update* re-approves the
#: item, so every metadata write that restores timestamps/authorship would silently
#: discard it; the captured state is therefore folded into that same write
#: (live-probed: both fields are accepted, and no version is created).
_APPROVAL_FIELDS = {
    "OData__ModerationStatus": "_ModerationStatus",
    "OData__ModerationComments": "_ModerationComments",
}

#: Approval status of an approved item (0 = draft/pending, 1 = rejected, 2 = approved).
#: A freshly uploaded document is approved, so only the other states are worth writing.
_APPROVED_STATUS = "2"

#: Moderation columns of a list item. They only exist on a list whose
#: ``EnableModeration`` is on, so selecting them unconditionally fails outright.
_MODERATION_FIELDS = ("OData__ModerationStatus", "OData__ModerationComments")

#: How many paths a per-run warning names before it summarizes the rest.
_WARNING_SAMPLE = 5

#: Multi-value typed columns. Their ``<name>Id`` companion is a collection of ids
#: that a ``*`` projection omits (LookupMulti entirely; UserMulti unreliably), so the
#: source selects them explicitly and the target writes ``{"results": [...]}``.
_MULTI_VALUE_TYPES = frozenset({"LookupMulti", "UserMulti"})

#: Typed columns whose values are remapped (lookup item ids, person logins).
_TYPED_VALUE_TYPES = frozenset({"Lookup", "LookupMulti", "User", "UserMulti"})

#: Properties the source column scans need. Selecting them explicitly keeps the read
#: independent of whatever ``$select`` a previous caller left on the shared
#: ``fields`` collection — ``List.fields`` survives a ``capture_list_structure``
#: read (which selects a different, narrower set), and a field payload that omits
#: ``AllowMultipleValues`` makes a multi-value column look single-value.
_SOURCE_FIELD_SELECT = [
    "Id",
    "InternalName",
    "TypeAsString",
    "SchemaXml",
    "Hidden",
    "ReadOnlyField",
    "TextField",
    "AllowMultipleValues",
]


#: Choice column types; a multi-choice column stores a collection of strings.
_CHOICE_TYPES = frozenset({"Choice", "MultiChoice"})

#: Column types whose value is a small REST object instead of a scalar.
_VALUE_OBJECT_TYPES = frozenset({"URL"})


def _allows_multiple_values(field: Any) -> bool:
    """Whether a Lookup/Person column holds many values.

    ``TypeAsString`` is not authoritative here. A column created from a
    ``Type="Lookup" Mult="TRUE"`` (or ``Type="User" Mult="TRUE"``) schema keeps that
    spelling, so SharePoint reports the *single-value* type and only
    ``AllowMultipleValues`` tells the truth (live-verified). Classifying such a
    column as single-value left its collection of ids unremapped: a multi-lookup
    kept source item ids and a multi-person kept source site-user ids on the target,
    and verification could not see the difference.
    """
    if getattr(field, "type_as_string", None) in _MULTI_VALUE_TYPES:
        return True
    return field.properties.get("AllowMultipleValues") is True


def _is_multi_choice_column(field: Any) -> bool:
    """Whether a Choice column stores a collection of values.

    ``TypeAsString == "MultiChoice"`` is the only reliable signal. Live-probed: a
    column created from a ``Type="Choice" Mult="TRUE"`` schema reads back as
    ``"Choice"``, stores one value in a single ``nvarchar`` slot (a scalar write
    round-trips, an array is rejected) and does not project ``AllowMultipleValues``
    at all — its schema ``Mult`` flag is misleading, so it is deliberately not used.
    """
    field_type = getattr(field, "type_as_string", None)
    if field_type == "MultiChoice":
        return True
    return field_type in _CHOICE_TYPES and _allows_multiple_values(field)


def _is_value_object_column(field: Any) -> bool:
    """Whether a column holds a REST value object rather than a scalar.

    A Hyperlink column is the common case: a read returns
    ``{"Url": ..., "Description": ...}``, which a scalar-only record projection
    dropped (a plain string is accepted on write but then makes every subsequent
    *read* of the column fail, live-probed).
    """
    return getattr(field, "type_as_string", None) in _VALUE_OBJECT_TYPES


def _scalar_mapping(value: Any) -> dict | None:
    """A value object as a plain mapping with scalar members, or ``None``.

    Only a shallow mapping of scalars is accepted, so a navigation property (a
    ``ClientObject``) or a typed payload carrying a nested ``__metadata`` is never
    mistaken for a column value.
    """
    if not isinstance(value, dict) or not value:
        return None
    if any(item is not None and not isinstance(item, (str, int, float, bool)) for item in value.values()):
        return None
    return dict(value)


#: Record columns excluded from the content checksum: server-assigned identity
#: (``Id``/``GUID``), facets verified separately (timestamps, authorship,
#: permissions), values the target remaps (``ContentTypeId``), and bookkeeping
#: (version label, server-derived embed URLs, the navigation ``ParentList``). What
#: remains is the item's *content* columns, which a faithful copy preserves.
_CONTENT_EXCLUDED = frozenset(
    {
        "Id",
        "ID",
        "GUID",
        "FileSystemObjectType",
        "Created",
        "Modified",
        "AuthorId",
        "EditorId",
        "HasUniqueRoleAssignments",
        "ContentTypeId",
        "OData__UIVersionString",
        "_UIVersionString",
        "ServerRedirectedEmbedUri",
        "ServerRedirectedEmbedUrl",
        "ParentList",
        "AttachmentFiles",
    }
)

#: Field types whose value is server-derived: a computed column (a link filename, a
#: doc icon) is a view of the item's identity, not metadata a folder carries.
_FOLDER_COMPUTED_TYPES = frozenset({"Attachments", "Computed", "File", "WorkflowStatus"})


def _folder_value_columns(fields: list[Any]) -> set[str]:
    """The columns a folder's own metadata can live in (writable, non-system).

    A read of a folder also returns computed and read-only columns (link filenames,
    compliance flags, version labels); writing those is rejected and comparing them
    would only echo the folder's own name back.
    """
    return {
        field.internal_name
        for field in fields
        if field.internal_name
        # An underscore-prefixed internal name is SharePoint's own storage column; it
        # is not reliably projectable (the same rule the safe fallback projection uses).
        and not field.internal_name.startswith("_")
        and not field.hidden
        and not field.read_only_field
        and field.type_as_string not in _FOLDER_COMPUTED_TYPES
        and field.internal_name not in _FOLDER_RECORD_EXCLUDED
    }


#: Folder (document library) record columns that never travel to the target: the
#: server-assigned identity and path columns, system metadata (restored by the
#: fidelity steps), and the folder-specific bookkeeping a read projects. A
#: ``ContentTypeId`` is kept — a document set's content type is part of what makes
#: the folder what it is.
_FOLDER_RECORD_EXCLUDED = (_CONTENT_EXCLUDED - {"ContentTypeId"}) | {
    "FileRef",
    "FileDirRef",
    "FileLeafRef",
    "FSObjType",
    "UniqueId",
    "SortBehavior",
    "SMTotalFileStreamSize",
    "SMTotalFileCount",
}


def _content_checksum(record: dict, extra_excluded: "frozenset[str]" = frozenset()) -> str:
    """MD5 of an item's content columns in a stable, order-independent form.

    The list source and target both use this so record content can be reconciled:
    only scalar, multi-value and value-object columns are hashed (navigation
    properties and excluded keys are dropped) and keys are sorted, so the two sides
    agree regardless of property iteration order. A null column is treated as
    absent: the source drops an empty multi-value column while the target reads it
    back as ``None``, and both mean "no value".
    """
    content = {}
    for key, value in record.items():
        if key in _CONTENT_EXCLUDED or key in extra_excluded or value is None:
            continue
        if isinstance(value, (str, int, float, bool, list, tuple)):
            content[key] = value
            continue
        mapping = _scalar_mapping(value)
        if mapping is not None:
            content[key] = mapping
    payload = json.dumps(content, sort_keys=True, default=str)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def _folder_record_values(record: dict) -> dict:
    """The column values of a folder item that travel to (or compare with) the target.

    The projection already narrows the read to the folder's own writable columns; here
    only the identity/system columns are dropped, and an empty value is treated as
    absent on both sides — a source read reports ``""`` where a target read reports
    ``None``, and both mean "no value".
    """
    return {
        key: value for key, value in record.items() if key not in _FOLDER_RECORD_EXCLUDED and value not in (None, "")
    }


def _id_list(value: Any) -> list[Any] | None:
    """Normalize a multi-value ``...Id`` collection into a plain list of ids.

    A live read returns the collection as a positional mapping (``{0: 1, 1: 2}``);
    a payload this client built may hold ``{"results": [...]}``. Both reduce to the
    same list, which is the form the checksum and the remap work with.
    """
    if isinstance(value, dict):
        if "results" in value:
            value = value["results"]
        else:
            try:
                return [value[i] for i in range(len(value))]
            except (KeyError, TypeError):
                return list(value.values())
    if isinstance(value, (list, tuple)):
        return list(value)
    return None


def _multi_values(value: Any) -> list[Any] | None:
    """A multi-value cell as a plain list of its values, or ``None`` when empty.

    Accepts every shape a live read or a built payload produces: a positional
    mapping (``{0: "red", 1: "green"}``), a ``{"results": [...]}`` wrapper, a bare
    list, and — because a collection cell may hold exactly one selection — a bare
    scalar.
    """
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return [value]
    return _id_list(value)


def _taxonomy_terms(value: Any) -> list[dict[str, str]]:
    """Normalize a taxonomy value to portable ``{"TermGuid": ...}`` terms.

    A live read shapes a single value as a dict (``{"Label", "TermGuid", "WssId"}``)
    and a multi-value one as a positional mapping (``{0: {...}, 1: {...}}``); a
    payload this client built holds a bare list. All reduce to a list of terms.
    Only ``TermGuid`` is carried: a per-site ``WssId`` is meaningless elsewhere and
    ``Label`` is not authoritative (a read may return the WssId string, and the
    server resolves a write by term id regardless of the label).
    """
    if value is None:
        return []
    if isinstance(value, dict):
        if "TermGuid" in value:
            items: list[Any] = [value]
        elif "results" in value and isinstance(value["results"], (list, tuple)):
            items = list(value["results"])
        else:
            try:
                items = [value[i] for i in range(len(value))]
            except (KeyError, TypeError):
                items = list(value.values())
    elif isinstance(value, (list, tuple)):
        items = list(value)
    else:
        return []
    terms: list[dict[str, str]] = []
    for item in items:
        if isinstance(item, dict):
            guid = item.get("TermGuid")
        else:
            guid = getattr(item, "TermGuid", None)
        if guid:
            terms.append({"TermGuid": str(guid)})
    return terms


def _is_taxonomy_value(value: Any) -> bool:
    """Whether a projected value is a taxonomy term (single dict or multi mapping/list)."""
    return isinstance(value, (dict, list, tuple)) and bool(_taxonomy_terms(value))


def _taxonomy_guids(value: Any) -> list[str]:
    return [term["TermGuid"] for term in _taxonomy_terms(value)]


def _canonicalize_taxonomy_record(record: dict) -> dict:
    """Replace taxonomy values with a sorted list of term ids for comparison.

    ``Label`` is cosmetic and ``WssId`` is site-local, so neither belongs in the
    content checksum; the term id is the portable identity. Sorting also keeps the
    checksum independent of the order a read happens to return the terms in.
    """
    if not any(_is_taxonomy_value(value) for value in record.values()):
        return record
    canonical = dict(record)
    for key, value in record.items():
        if _is_taxonomy_value(value):
            canonical[key] = sorted(_taxonomy_guids(value))
    return canonical


def _collection_payload(ids: list) -> dict:
    """The JSON shape SharePoint accepts when *creating* a multi-value column.

    Live-probed: a bare array is rejected on create
    (``InvalidClientQueryException``: "a 'PrimitiveValue' or 'StartObject' node was
    expected") while ``{"results": [...]}`` is accepted. A MERGE *update* is the
    opposite — it accepts the bare array and rejects ``{"results": [...]}`` — so
    only the create path goes through this helper.
    """
    return {"results": ids}


def _sp_utc_timestamp(value: str | None) -> str | None:
    """Normalize a timestamp to the UTC form a *list item* honors.

    Live-probed: ``ValidateUpdateListItem`` on a plain list item parses an
    ISO-8601 value with a trailing ``Z`` as UTC (and ``datesInUTC=True`` keeps it
    that way), so this form round-trips the exact instant.
    """
    if not value:
        return None
    parsed = parse_datetime(value)
    if parsed is None:
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sp_local_timestamp(value: datetime | str | None) -> str | None:
    """Format a *web-local* value as the date form a document item accepts.

    Live-probed: document-library items ignore ``datesInUTC`` and parse every date
    string in the web's locale, rejecting a trailing ``Z`` (``...must specify a
    valid date within the range of 1/1/1900 and 12/31/8900.``). The space-separated
    ``YYYY-MM-DD HH:MM:SS`` form is accepted and interpreted as local wall-clock,
    so callers must pass the instant already converted to web-local time (see
    ``SharePointLibraryTarget._local_timestamp``).
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _report_rejected_fields(result, warnings: list[str], label: str) -> None:
    """Warn about ``ValidateUpdateListItem`` fields the server rejected.

    A rejected field does not raise over HTTP — the response carries a per-field
    ``HasException``/``ErrorMessage`` — and worse, SharePoint rolls the whole batch
    back, so a sibling ``Created``/``Modified`` write is discarded too. Surfacing it
    keeps that invisible loss honest (and testable).
    """
    values = getattr(result, "value", None) or []
    for value in values:
        if getattr(value, "HasException", False):
            warnings.append(f"{label}: {value.FieldName} rejected ({value.ErrorMessage})")


def _moderation_state(properties: dict) -> dict:
    """The approval fields of a list item, in ``ValidateUpdateListItem`` form.

    Only present ones are returned: an empty ``_ModerationComments`` normalizes to
    ``None`` server-side, so a blank comment is not carried.
    """
    status = properties.get("OData__ModerationStatus")
    state: dict = {}
    if status is not None:
        state["_ModerationStatus"] = str(status)
    comments = properties.get("OData__ModerationComments")
    if comments:
        state["_ModerationComments"] = str(comments)
    return state


def _version_sort_key(label: str) -> tuple[int, ...]:
    """Sort key for a version label like ``"2.0"`` (numeric parts, non-numeric last)."""
    try:
        return tuple(int(part) for part in str(label).split("."))
    except ValueError:
        return (0,)


#: Library-relative paths SharePoint owns and recreates on the target (its forms
#: folder and the folder rendering file). Migrating them collides server-side and
#: clobbers system pages client-side, so the source adapter skips them.
_LIBRARY_SYSTEM_PATHS = ("Forms", "desktop.ini")

#: SiteAssets is the one library that also holds per-site infrastructure — the
#: site icon and the auto-provisioned OneNote folder.
_SITE_ASSETS_URL_SUFFIX = "/SiteAssets"


def _site_assets_scaffolding(folder) -> tuple[str, ...]:
    """SiteAssets-only SharePoint-owned entries for this web (empty otherwise).

    Every modern site provisions ``SiteAssets/<web title> Notebook``; migrating
    it (or reporting it) yields a phantom missing/extra pair because the target's
    folder carries the *target* web's name. The site icon is site branding whose
    bytes are meaningless on another site. Both are skipped on each side.
    """
    url = (folder.server_relative_url or "").rstrip("/")
    if not url.endswith(_SITE_ASSETS_URL_SUFFIX):
        return ()
    web = folder.context.web
    if not web.properties.get("Title"):
        web.ensure_properties(["Title"]).execute_query()
    title = web.title
    names = ["__siteIcon__.png"]
    if title:
        names.append(f"{title} Notebook")
    return tuple(names)


def _is_system_path(rel: str, extra: tuple[str, ...] = ()) -> bool:
    """Whether a library-relative path is SharePoint-owned scaffolding, not user content."""
    entries = (*_LIBRARY_SYSTEM_PATHS, *extra)
    return any(rel == entry or rel.startswith(entry + "/") for entry in entries)


def is_taxonomy_validation(exc: Exception) -> bool:
    """True when a request failed because a Managed Metadata (taxonomy) column
    references a term set / term that no longer exists.

    SharePoint raises ``SPFieldValidationException`` ("the given guid does not
    exist in the term store") while composing the item payload — the exact case
    that makes a plain list-items read fail.
    """
    text = f"{getattr(exc, 'code', '') or ''} {getattr(exc, 'message', '') or ''} {exc}".lower()
    return "spfieldvalidationexception" in text and "term store" in text


def taxonomy_internal_names(fields) -> list[str]:
    """Internal names of Managed Metadata columns in a loaded field set."""
    names: list[str] = []
    for field in fields:
        type_name = getattr(field, "type_as_string", None) or ""
        schema = getattr(field, "schema_xml", None) or ""
        if type_name in _TAXONOMY_FIELD_TYPES or "TermSetId=" in schema:
            internal_name = getattr(field, "internal_name", None)
            if internal_name:
                names.append(internal_name)
    return list(dict.fromkeys(names))


def _perm_mask(role_definition: Any) -> str | None:
    """The decimal ``PermMask`` of a role definition (``BasePermissions`` High/Low)."""
    base = getattr(role_definition, "base_permissions", None)
    if base is None:
        return None
    try:
        return str((int(base.High) << 32) | int(base.Low))
    except (TypeError, ValueError):
        return None


def _is_user_principal(member: Any) -> bool:
    """Whether a role-assignment member is a user (not a group)."""
    ptype = getattr(member, "principal_type", None)
    if ptype is None:
        return False
    if ptype == PrincipalType.User:
        return True
    # ``PrincipalType`` is a plain ``Enum`` (not ``IntEnum``); accept a raw int too.
    return getattr(ptype, "value", ptype) == PrincipalType.User.value


def _is_system_principal(user: Any) -> bool:
    """Whether a resolved user is a tenant system/app account.

    The Migration API cannot set ``Author``/``Editor`` to a system account, and a
    ``ValidateUpdateListItem`` batch containing one is rejected wholesale — which
    would silently discard the ``Created``/``Modified`` restoration we send in the
    same call. Items created by the migration app itself are authored by such an
    account, so setting it is a no-op anyway; skipping it keeps the timestamp write
    intact.
    """
    login = (getattr(user, "login_name", None) or "").lower()
    return "app@sharepoint" in login or "sharepoint\\system" in login


def _has_unique_role_assignments(securable, *, refresh: bool = False) -> bool:
    """Whether a securable has unique (broken-inheritance) role assignments.

    SharePoint REST returns *inherited* role assignments too, so reading them
    verbatim would break inheritance on every item and replicate the parent ACL.
    Only items with unique assignments are read/applied (and compared by the
    verifier); inherited items stay inherited on the target.

    A plain entity read does not return the flag, so an object loaded *before* its
    ACL changed keeps a stale value. The target side passes ``refresh=True``: this
    value decides whether an ACL is applied or compared at all, so a stale
    ``False`` would break inheritance on an item that is already unique (wiping the
    assignments it was supposed to keep) and a stale ``False`` read back after a
    write would report a permission mismatch for an ACL that did land.
    """
    unique = getattr(securable, "has_unique_role_assignments", None)
    if unique is not None and not refresh:
        return bool(unique)
    options = getattr(securable, "query_options", None)
    previous = list(getattr(options, "select", None) or [])
    try:
        securable.select(["HasUniqueRoleAssignments"]).get().execute_query()
    except Exception:  # noqa: BLE001 — an unreadable flag is treated as "not unique"
        return False
    finally:
        if options is not None:
            # The projection lives on the object's query options: leaving it on
            # would narrow every later read of the same item.
            options.select = previous
    return bool(securable.properties.get("HasUniqueRoleAssignments"))


def _replay_role_assignments(
    securable,
    principals: "_TargetPrincipals",
    permissions: list[PermissionEntry],
    warnings: list[str],
    label: str,
) -> None:
    """Replay an item's unique ACLs onto a target item: additive, never destructive.

    Every principal is resolved on the target first (users via ``EnsureUser``,
    groups by name, default groups by role kind). Inheritance is broken only when
    the target item still inherits *and* at least one assignment resolved: an item
    whose every principal is unresolvable (a cross-tenant account, an app
    principal) would otherwise end up with an **empty** ACL — inheritance broken,
    nobody granted — which is worse than leaving it inheriting, so that case is
    reported and the item is left alone.

    A re-run therefore adds only what is missing and never removes an assignment
    the source does not grant. The caller executes the queued requests.
    """
    resolved: list[tuple[Any, Any]] = []
    for entry in permissions:
        principal = principals.principal(entry.principal_name)
        if principal is None:
            continue
        for role_name in entry.roles:
            role = principals.role(role_name)
            if role is None:
                warnings.append(f"permissions {label}: could not resolve role {role_name!r}")
                continue
            resolved.append((principal, role))
    if not resolved:
        warnings.append(
            f"permissions for {label!r} were not restored: no assignment could be resolved on the "
            "target, and breaking inheritance would leave the item with an empty ACL — it still inherits"
        )
        return
    if not _has_unique_role_assignments(securable, refresh=True):
        securable.break_role_inheritance(copy_role_assignments=False, clear_sub_scopes=False)
    for principal, role in resolved:
        securable.add_role_assignment(principal, role)


def _user_login(web, user_id: Any, cache: dict[int, str | None]) -> str | None:
    """Resolve a target user id to its login name, cached."""
    key = parse_int(user_id)
    if key is None:
        return None
    if key in cache:
        return cache[key]
    login: str | None = None
    try:
        user = web.site_users.get_by_id(key).get().execute_query()
        login = user.login_name or None
    except Exception:  # noqa: BLE001 — an unresolvable id yields no login
        login = None
    cache[key] = login
    return login


class _MultiValueCreateTarget:
    """An upsert target that reshapes multi-value columns only when creating.

    A multi-value Lookup/Person column is created with the ``{"results": [...]}``
    wire shape but updated with a bare array (live-probed), so ``keyed_queue`` needs
    to reshape the creates and leave the updates alone. Everything else delegates.
    """

    def __init__(self, target: Any, reshape: Callable[[dict], dict]) -> None:
        self._target = target
        self._reshape = reshape

    @property
    def key_field(self) -> str:
        return self._target.key_field

    def ensure_key_field(self) -> None:
        self._target.ensure_key_field()

    def load_keys(self) -> Any:
        return self._target.load_keys()

    def create_records(self, records: list[dict]) -> None:
        self._target.create_records([self._reshape(record) for record in records])

    def update_record(self, item_id: Any, record: dict) -> None:
        self._target.update_record(item_id, record)


class _DefaultGroups:
    """Maps a web's associated default groups (Owners/Members/Visitors).

    Default groups are titled after the site (``team Owners``), so a source and
    target in the same tenant rarely share the exact name. These groups are used
    both to resolve a source name onto the target *and* to normalize the name to a
    canonical ``default:<Kind>`` token so the permission diff compares like with
    like (a renamed site still verifies as preserved). Loaded once, lazily.
    """

    ATTRS = (
        ("Owners", "associated_owner_group"),
        ("Members", "associated_member_group"),
        ("Visitors", "associated_visitor_group"),
    )

    def __init__(self, web) -> None:
        self._web = web
        self._by_kind: dict[str, Any] | None = None
        self._by_title: dict[str, str] = {}

    def _load(self) -> None:
        if self._by_kind is not None:
            return
        self._by_kind = {}
        for kind, attr in self.ATTRS:
            group = getattr(self._web, attr, None)
            if group is None:
                continue
            try:
                group.get().execute_query()
            except Exception:  # noqa: BLE001 — an unreadable group is skipped
                continue
            self._by_kind[kind] = group
            title = getattr(group, "title", None) or getattr(group, "login_name", None)
            if title:
                self._by_title[title] = kind

    def group(self, kind: str):
        self._load()
        return self._by_kind.get(kind) if self._by_kind else None

    def normalize(self, name: str) -> str:
        self._load()
        kind = self._by_title.get(name)
        return f"default:{kind}" if kind else name


class _TargetPrincipals:
    """Resolve source principals and role definitions on a target web (cached).

    Users are ensured on the site (``EnsureUser``) so their numeric id can be used
    for authorship and role assignments; groups are matched by name, and the
    default SharePoint groups (Owners/Members/Visitors) fall back to the target
    web's associated groups so a renamed site (``team`` -> ``team_out``) still
    maps its role assignments. Anything that cannot be resolved is skipped with a
    warning (same-tenant, best-effort).
    """

    def __init__(self, web, warnings: list[str]) -> None:
        self._web = web
        self._warnings = warnings
        self._users: dict[str, Any] = {}
        self._roles: "dict[str, RoleDefinition] | None" = None
        self._defaults = _DefaultGroups(web)

    @staticmethod
    def _strip_claims(name: str) -> str:
        return name.rsplit("|", 1)[-1] if name.startswith("i:0#") else name

    def normalize(self, name: str) -> str:
        """Canonical principal name (default groups collapse to ``default:<Kind>``)."""
        return self._defaults.normalize(name)

    def user(self, login: str | None):
        """Ensure a user login on the target site and return its ``User`` object."""
        if not login:
            return None
        login = self._strip_claims(login)
        if login in self._users:
            return self._users[login]
        obj = None
        try:
            obj = self._web.ensure_user(login).execute_query()
        except Exception as e:  # noqa: BLE001 — an unresolvable principal is skipped
            self._warnings.append(f"could not ensure target user {login!r}: {e}")
        self._users[login] = obj
        return obj

    def principal(self, name: str):
        """Resolve a source principal (user or group) to a target principal object."""
        if not name:
            return None
        login = self._strip_claims(name)
        if login.startswith("default:"):
            return self._defaults.group(login.split(":", 1)[1])
        if "@" in login:
            return self.user(login)
        group = None
        try:
            group = self._web.site_groups.get_by_name(login).get().execute_query()
        except Exception:  # noqa: BLE001 — fall back to the default groups below
            group = None
        if group is None:
            kind = login.rsplit(" ", 1)[-1]
            if kind in {"Owners", "Members", "Visitors"}:
                group = self._defaults.group(kind)
        if group is not None:
            return group
        self._warnings.append(f"could not resolve principal {name!r} on the target")
        return None

    def role(self, name: str) -> "RoleDefinition | None":
        """Resolve (and cache) a target role definition by name."""
        if self._roles is None:
            loaded = self._web.role_definitions.get().execute_query()
            self._roles = {rd.name: rd for rd in loaded if rd.name}
        return self._roles.get(name)


def _read_role_assignments(
    securable,
    resolve: Callable[[Any], "Principal | None"] | None = None,
    normalize: Callable[[str], str] | None = None,
) -> list[PermissionEntry]:
    """Read a securable object's role assignments into ``PermissionEntry``s.

    One entry per principal (user or group), keyed by login name; the target uses
    the same shape so the permission diff compares like with like. ``normalize``
    (when supplied) canonicalizes a principal name — default groups collapse to
    ``default:<Kind>`` so a renamed site still compares as preserved. Role names are
    paired with their decimal ``PermMask`` (``role_masks``), and — when ``resolve``
    is supplied — a user principal is enriched with its PUID/display name/email so
    the server-side package target can emit a faithful ``UserGroup.xml`` entry.
    """
    assignments = securable.role_assignments.expand(["Member", "RoleDefinitionBindings"]).get().execute_query()
    result: list[PermissionEntry] = []
    for assignment in assignments:
        member = assignment.member
        name = member.login_name or member.user_principal_name
        if not name:
            continue
        roles: list[str] = []
        role_masks: dict[str, str] = {}
        for role in assignment.role_definition_bindings:
            if not role.name:
                continue
            roles.append(role.name)
            mask = _perm_mask(role)
            if mask is not None:
                role_masks[role.name] = mask
        entry = PermissionEntry(
            principal_name=normalize(name) if normalize is not None else name,
            roles=roles,
            role_masks=role_masks,
        )
        if resolve is not None and _is_user_principal(member):
            principal = resolve(getattr(member, "id", None))
            if principal is not None:
                entry.system_id = principal.system_id
                entry.display_name = principal.display_name
                entry.email = principal.email
        result.append(entry)
    return result


class SharePointListSource:
    """Enumerates a SharePoint list's items into record migration items."""

    # Marks this source as emitting list-item attachments as extra items (see DataSource).
    supports_attachments = True

    # Marks this source as annotating Person columns with a portable login name so the
    # target can resolve them (see ``_annotate_person_logins``).
    supports_typed_values = True

    def rebind(self) -> "SharePointListSource":
        """This source on its own cloned context, so another thread can drive it.

        A context owns one pending-query queue: two adapters sharing it interleave
        their deferred queries. Re-addressing the same list (by id) on a ``clone``
        — which shares the authenticated transport — lets a session run several
        list jobs in parallel over one connection pool. Read caches are per-run and
        deliberately not carried over.
        """
        return SharePointListSource(_cloned_list(self._list), self._select)

    def __init__(self, source_list: "SPList", select: list[str] | None = None) -> None:
        self._list = source_list
        self._select = select
        self._records: dict[str, dict] = {}
        self._items: dict[str, Any] = {}
        self._attachments: dict[str, Any] = {}
        self._users: dict[int, Principal | None] = {}
        self._default_groups: _DefaultGroups | None = None
        self._source_fields_cache: list[Any] | None = None
        self._user_columns_cache: set[str] | None = None
        self._multi_columns_cache: dict[str, str] | None = None
        self._skipped_columns_cache: set[str] | None = None
        self._taxonomy_columns_cache: dict[str, bool] | None = None
        self._taxonomy_note_columns_cache: set[str] | None = None
        self._multi_choice_columns_cache: set[str] | None = None
        self._value_object_columns_cache: set[str] | None = None
        self._folder_records_cache: dict[str, dict] | None = None
        self.warnings: list[str] = []

    def label(self) -> str:
        return f"list:{self._list.title}"

    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        try:
            loaded = self._load_items(self._select)
        except Exception as e:  # noqa: BLE001 — see the taxonomy fallback below
            # A full read of a list with an orphaned Managed Metadata column
            # fails server-side; re-enumerate excluding those columns instead
            # of aborting the export. An explicit --select is honored as-is.
            if not is_taxonomy_validation(e) or self._select:
                raise
            self.warnings.append(
                "Full item read failed — a Managed Metadata column references a missing term set; "
                "re-read with taxonomy columns excluded."
            )
            try:
                loaded = self._load_items(self._safe_select())
            except Exception:
                # Some visible columns can still be denied to the principal;
                # fall back to the smallest possible projection.
                self.warnings.append("visible-column read denied too — exporting Id/Title only")
                loaded = self._load_items(["Id", "Title"])
        return self._project(loaded, progress)

    def _load_items(self, select: list[str] | None, folder_only: bool = False):
        items = self._list.items
        # A full read projects ``*`` plus the system metadata so author/editor ids
        # and the unique-ACL flag are captured in one query (``*`` omits them);
        # an explicit/safe projection is honored as-is.
        if select is None:
            columns = ["*", *_METADATA_SELECT]
            # A ``*`` projection also omits multi-value Lookup ids (and returns
            # multi-person ids only inconsistently); select each ``<name>Id``
            # explicitly so the values are not silently lost.
            for name in self._multi_columns():
                key = f"{name}Id"
                if key not in columns:
                    columns.append(key)
            # Expand attachments so they can be migrated alongside their item.
            query = items.select(columns).expand(["AttachmentFiles"])
            if folder_only:
                query = query.filter("FSObjType eq 1")
            return query.get_all().execute_query()
        query = items.select(select)
        if folder_only:
            query = query.filter("FSObjType eq 1")
        return query.get_all().execute_query()

    def _safe_select(self) -> list[str]:
        """Fallback projection: visible, non-system columns minus Managed Metadata.

        Selecting hidden/system columns (``_Shortcut*``, ``MainLinkSettings``,
        taxonomy companion fields, ...) can itself be denied, so the fallback
        stays on the list's user columns only.
        """
        fields = self._list.fields.get().execute_query()
        taxonomy = taxonomy_internal_names(fields)
        self.warnings.append(f"excluded Managed Metadata column(s): {', '.join(sorted(taxonomy)) or 'none'}")
        columns = ["Id"]
        for field in fields:
            internal_name = getattr(field, "internal_name", None)
            if not internal_name or internal_name in taxonomy or internal_name in columns:
                continue
            if internal_name.startswith("_") or getattr(field, "hidden", False):
                continue  # hidden/system metadata — not safe to project
            if internal_name in SYSTEM_FIELD_NAMES:
                continue
            columns.append(internal_name)
        return columns

    def _project(self, loaded, progress: MigrationProgress) -> list[MigrationItem]:
        records = self._project_records(loaded)
        result: list[MigrationItem] = []
        pending_attachments: list[tuple[str, Any]] = []
        for item, record in zip(loaded, records):
            item_id = str(item.id)
            self._records[item_id] = record
            self._items[item_id] = item
            author_id = parse_int(record.get("AuthorId"))
            editor_id = parse_int(record.get("EditorId"))
            planned = MigrationItem(
                source_path=f"{self._list.title}/{item_id}",
                dest_path=item_id,
                item_type="record",
                modified=iso_or_none(record.get("Modified")),
                created=iso_or_none(record.get("Created")),
                author_id=author_id,
                editor_id=editor_id,
            )
            # Resolve the source author/editor once so an authorship-preserving
            # target can restore them by login name (ids are tenant-local).
            if author_id is not None:
                planned.author = self._principal_for(author_id)
            if editor_id is not None:
                planned.editor = self._principal_for(editor_id)
            result.append(planned)
            for attachment in item.properties.get("AttachmentFiles") or []:
                pending_attachments.append((item_id, attachment))
            emit_progress(progress, done=len(result), stage="planning", items=[item])
        # Attachments come after every record so the target can create all parent
        # items before it resolves and uploads their attachments.
        for item_id, attachment in pending_attachments:
            name = getattr(attachment, "file_name", None)
            if not name:
                self.warnings.append(f"skipped an attachment without a file name on item {item_id}")
                continue
            dest_path = f"{item_id}/{name}"
            self._attachments[dest_path] = attachment
            result.append(
                MigrationItem(
                    source_path=f"{self._list.title}/{dest_path}",
                    dest_path=dest_path,
                    item_type="attachment",
                )
            )
            emit_progress(progress, done=len(result), stage="planning", items=[attachment])
        return result

    def _project_records(self, loaded, report_skipped: bool = True) -> list[dict]:
        # Project every loaded property — not the collection's literal ``select``.
        # Passing ``["*", ...]`` straight through emitted ``{"*": None, ...}``, so
        # migrated records carried no field values at all. ``AttachmentFiles`` is a
        # navigation property (objects, not a scalar column) and is excluded; the
        # target writes attachments separately.
        select = sorted(
            {key for item in loaded for key in item.properties if key != "AttachmentFiles"} - _NON_WRITABLE_SELECT
        )
        records = records_from_items(list(loaded), select, set(), raw=True)
        # A REST item create accepts scalar column values only. A full read also
        # returns navigation properties (``ParentList``) and typed values
        # (lookups/persons, e.g. ``PredecessorsId`` / ``AssignedTo``) whose JSON
        # objects carry no ``__metadata.type`` here, so the create batch is
        # rejected with ``InvalidClientQueryException``. Typed-value remapping is
        # not supported yet, so drop them and say so rather than fail the run.
        dropped: set[str] = set()
        multi = self._multi_columns()
        multi_keys = {f"{name}Id" for name in multi} | {f"{name}StringId" for name in multi}
        choices = self._multi_choice_columns()
        taxonomy = self._taxonomy_columns()
        value_objects = self._value_object_columns()
        for record in records:
            for key, value in list(record.items()):
                if key in multi_keys:
                    continue  # handled by ``_normalize_multi_values``
                if key in choices:
                    continue  # handled by ``_normalize_multi_choice_values``
                if key in taxonomy:
                    continue  # handled by ``_project_taxonomy_values``
                if key in value_objects and _scalar_mapping(value) is not None:
                    record[key] = _scalar_mapping(value)
                    continue  # a value object (``{"Url", "Description"}``) is writable as-is
                if value is not None and not isinstance(value, (str, int, float, bool)):
                    record.pop(key)
                    if key not in _NAVIGATION_SELECT:
                        dropped.add(key)
        if dropped:
            self.warnings.append(
                f"skipped non-scalar column(s) with no typed-value mapping: {', '.join(sorted(dropped))}"
            )
        # Structure provisioning skips hidden columns, so their typed values (and
        # the text companion) have nowhere to land on the target; drop both rather
        # than fail the create on an unknown column.
        skipped = self._skipped_columns()
        if skipped:
            skipped_keys = {f"{name}Id" for name in skipped} | {f"{name}StringId" for name in skipped}
            for record in records:
                for key in skipped_keys:
                    record.pop(key, None)
            if report_skipped:
                self.warnings.append(
                    f"skipped hidden typed column(s) not replicated by structure provisioning: "
                    f"{', '.join(sorted(skipped))}"
                )
        self._project_taxonomy_values(records)
        self._normalize_multi_values(records)
        self._normalize_multi_choice_values(records)
        self._annotate_person_logins(records)
        return records

    def folder_records(self) -> dict[str, dict]:
        """Column values of this list's folders, keyed by their server-relative URL.

        A document library's folders are list items too: a document set or a managed
        folder carries its own column values, so a target that only created the empty
        folder would silently lose them. The values go through the same projection as
        an item's (typed values normalized, system and navigation columns dropped), so
        the target can write them onto the folder's underlying item. The read is
        narrowed to the folder's writable columns (see :meth:`folder_projection`): a
        ``*`` read also returns system and computed columns (compliance flags, link
        filenames, version labels) that an update would reject and that carry no
        portable value.
        """
        if self._folder_records_cache is None:
            records: dict[str, dict] = {}
            try:
                loaded = self._load_items(self.folder_projection(), folder_only=True)
            except Exception as e:  # noqa: BLE001 — folder values are best-effort
                self.warnings.append(f"folder column values could not be read: {e}")
                loaded = []
            # The folder projection already excluded the columns an item record would
            # report as unmigratable, so those messages would describe nothing.
            for record in self._project_records(loaded, report_skipped=False) if loaded else []:
                url = record.get("FileRef")
                if not isinstance(url, str) or not url:
                    continue
                values = _folder_record_values(record)
                if values:
                    records[url.rstrip("/")] = values
            self._folder_records_cache = records
        return self._folder_records_cache

    def folder_projection(self) -> list[str]:
        """The columns that carry a folder's own metadata, plus what typed values need.

        A folder has no separate create payload: its values are read back as a record,
        written onto the folder's item and compared the same way — so the projection
        must include the companions the typed-value normalization reads (``<name>Id``
        for Lookup/Person values, the hidden note of a Managed Metadata column).
        """
        writable = _folder_value_columns(self._source_fields())
        # ``FileRef`` keys the record (it is the folder's identity, not a value).
        columns = ["ContentTypeId", "FileRef", *sorted(writable)]
        # Lookup and Person values are carried as item ids / logins under
        # ``<name>Id``; the column itself is carried in the record too.
        single_lookups = {
            field.internal_name
            for field in self._source_fields()
            if field.internal_name and field.type_as_string == "Lookup" and not _allows_multiple_values(field)
        }
        for name in sorted((single_lookups | self._user_columns() | set(self._multi_columns())) & writable):
            key = f"{name}Id"
            if key not in columns:
                columns.append(key)
        for note in self._taxonomy_note_columns():
            if note not in columns:
                columns.append(note)
        return columns

    def _source_fields(self) -> list[Any]:
        """The source list's field definitions, read once and shared by every scan."""
        if self._source_fields_cache is None:
            self._source_fields_cache = list(self._list.fields.select(list(_SOURCE_FIELD_SELECT)).get().execute_query())
        return self._source_fields_cache

    def _taxonomy_columns(self) -> dict[str, bool]:
        """The source's Managed Metadata columns (internal name -> allows many)."""
        if self._taxonomy_columns_cache is None:
            columns: dict[str, bool] = {}
            notes: set[str] = set()
            try:
                fields = self._source_fields()
                by_id = {
                    normalize_guid(getattr(field, "id", None)): getattr(field, "internal_name", None) for field in fields
                }
                for field in fields:
                    internal_name = getattr(field, "internal_name", None)
                    if not internal_name:
                        continue
                    field_type = getattr(field, "type_as_string", None)
                    schema = getattr(field, "schema_xml", None) or ""
                    if field_type not in _TAXONOMY_FIELD_TYPES and "TermSetId" not in schema:
                        continue
                    columns[internal_name] = field_type == "TaxonomyFieldTypeMulti" or 'Mult="TRUE"' in schema
                    note = by_id.get(normalize_guid(field.properties.get("TextField")))
                    if note:
                        notes.add(note)
            except Exception as e:  # noqa: BLE001 — values stay un-remapped, never fatal
                self.warnings.append(f"could not read source columns for taxonomy remapping: {e}")
            self._taxonomy_columns_cache = columns
            self._taxonomy_note_columns_cache = notes
        return self._taxonomy_columns_cache

    def _taxonomy_note_columns(self) -> set[str]:
        """The hidden note companions of the source's taxonomy columns."""
        self._taxonomy_columns()
        return self._taxonomy_note_columns_cache or set()

    def _project_taxonomy_values(self, records: list[dict]) -> None:
        """Project taxonomy columns as bare ``[{"TermGuid": ...}]`` term lists.

        The target recreates the column against the same term set and rebuilds the
        write payload, so only the portable term id travels. The hidden note
        companion (if a projection happens to include it) is dropped.
        """
        columns = self._taxonomy_columns()
        if not columns:
            return
        notes = self._taxonomy_note_columns()
        for record in records:
            for note in notes:
                record.pop(note, None)
            for name in columns:
                terms = _taxonomy_terms(record.get(name))
                if terms:
                    record[name] = terms
                else:
                    record.pop(name, None)

    def _typed_columns(self) -> tuple[set[str], dict[str, str], set[str]]:
        """The source's Person and multi-value columns, read once.

        Returns ``(single-value User columns, {multi-value column: field type},
        hidden typed columns)``. The field type tells a multi-lookup (remapped by
        item id) from a multi-person (remapped by login). Hidden typed columns are
        reported separately because structure provisioning does not replicate them.
        """
        if self._user_columns_cache is None or self._multi_columns_cache is None or self._skipped_columns_cache is None:
            users: set[str] = set()
            multi: dict[str, str] = {}
            skipped: set[str] = set()
            try:
                for field in self._source_fields():
                    internal_name = getattr(field, "internal_name", None)
                    if not internal_name or internal_name in _PERSON_EXCLUDED:
                        continue
                    field_type = getattr(field, "type_as_string", None)
                    if field_type not in _TYPED_VALUE_TYPES:
                        continue
                    # Structure replay skips hidden columns, so the target never
                    # gets them; projecting their values would fail the write.
                    if getattr(field, "hidden", None) is True:
                        skipped.add(internal_name)
                    elif field_type.startswith("User"):
                        if _allows_multiple_values(field):
                            multi[internal_name] = "UserMulti"
                        else:
                            users.add(internal_name)
                    elif _allows_multiple_values(field):
                        multi[internal_name] = "LookupMulti"
            except Exception as e:  # noqa: BLE001 — without field types ids stay raw
                self.warnings.append(f"could not read source columns for typed-value remapping: {e}")
            self._user_columns_cache = users
            self._multi_columns_cache = multi
            self._skipped_columns_cache = skipped
        return self._user_columns_cache, self._multi_columns_cache, self._skipped_columns_cache

    def _user_columns(self) -> set[str]:
        """The source's single-value Person columns (internal names)."""
        return self._typed_columns()[0]

    def _multi_columns(self) -> dict[str, str]:
        """The source's multi-value Lookup/Person columns (internal name -> field type)."""
        return self._typed_columns()[1]

    def _skipped_columns(self) -> set[str]:
        """The source's hidden Person/multi-value columns (not replicated on the target)."""
        return self._typed_columns()[2]

    def _multi_choice_columns(self) -> set[str]:
        """The source's multi-choice columns (internal names)."""
        if self._multi_choice_columns_cache is None:
            names: set[str] = set()
            try:
                names = {
                    field.internal_name
                    for field in self._source_fields()
                    if getattr(field, "internal_name", None) and _is_multi_choice_column(field)
                }
            except Exception as e:  # noqa: BLE001 — values stay un-normalized, never fatal
                self.warnings.append(f"could not read source columns for multi-choice values: {e}")
            self._multi_choice_columns_cache = names
        return self._multi_choice_columns_cache

    def _value_object_columns(self) -> set[str]:
        """The source's columns that hold a REST value object (e.g. a hyperlink)."""
        if self._value_object_columns_cache is None:
            names: set[str] = set()
            try:
                names = {
                    field.internal_name
                    for field in self._source_fields()
                    if getattr(field, "internal_name", None) and _is_value_object_column(field)
                }
            except Exception as e:  # noqa: BLE001 — values are dropped, never fatal
                self.warnings.append(f"could not read source columns for value-object values: {e}")
            self._value_object_columns_cache = names
        return self._value_object_columns_cache

    def _annotate_person_logins(self, records: list[dict]) -> None:
        """Replace each Person column's site-user id with the user's login name.

        A site-user id is only meaningful inside its own site collection, so it is
        meaningless on the target. The login *is* portable, and the target resolves
        it back to (a possibly different) target site-user id with ``EnsureUser``.
        A person the source cannot resolve is dropped and reported rather than
        copied as a wrong id.
        """
        columns = self._user_columns()
        if not columns:
            return
        for record in records:
            for name in columns:
                # ``<name>StringId`` is a read-only text companion holding the user
                # id; leaving it in the payload makes REST ignore the remapped
                # ``<name>Id`` and keep the source id.
                record.pop(f"{name}StringId", None)
                key = f"{name}Id"
                user_id = parse_int(record.get(key))
                if user_id is None:
                    continue
                principal = self._principal_for(user_id)
                login = principal.login_name if principal else None
                if login:
                    record[key] = login
                else:
                    record.pop(key, None)
                    self.warnings.append(
                        f"person column '{name}' value {user_id} could not be resolved to a login; left empty"
                    )

    def _normalize_multi_values(self, records: list[dict]) -> None:
        """Project each multi-value column's ids as a plain list the target can remap.

        A multi-person column additionally carries the portable login names instead
        of the site-local ids, matching the single-value Person handling.
        """
        multi = self._multi_columns()
        if not multi:
            return
        for record in records:
            for name, field_type in multi.items():
                record.pop(f"{name}StringId", None)
                key = f"{name}Id"
                ids = _id_list(record.get(key))
                parsed: list[int] = []
                for value in ids or []:
                    user_id = parse_int(value)
                    if user_id is None:
                        parsed = []
                        break
                    parsed.append(user_id)
                if not parsed:
                    record.pop(key, None)
                    continue
                if field_type == "UserMulti":
                    logins: list[str] = []
                    for user_id in parsed:
                        principal = self._principal_for(user_id)
                        login = principal.login_name if principal else None
                        if login:
                            logins.append(login)
                        else:
                            self.warnings.append(
                                f"multi-person column '{name}' value {user_id} could not be resolved "
                                "to a login; the value was left out"
                            )
                    if logins:
                        record[key] = logins
                    else:
                        record.pop(key, None)
                else:
                    record[key] = parsed

    def _normalize_multi_choice_values(self, records: list[dict]) -> None:
        """Project each multi-choice column as a plain list of its selected values.

        A live read returns the collection as a positional mapping
        (``{0: "red", 1: "green"}``); the source records it as a bare list, which is
        what the checksum compares and what the target wraps for a create. An empty
        selection is dropped so the column reads back empty rather than as an empty
        collection.
        """
        names = self._multi_choice_columns()
        if not names:
            return
        for record in records:
            for name in names:
                if name not in record:
                    continue
                values = _multi_values(record.get(name))
                if values:
                    record[name] = values
                else:
                    record.pop(name, None)

    def read(self, item: MigrationItem) -> object:
        if item.item_type == "attachment":
            return self._attachment_content(item)
        return self._records.get(item.dest_path, {})

    def _attachment_content(self, item: MigrationItem) -> bytes:
        attachment = self._attachments.get(item.dest_path)
        if attachment is None:
            raise FileNotFoundError(item.source_path)
        return cast(bytes, attachment.get_content().execute_query().value)

    def checksum(self, item: MigrationItem) -> str:
        if item.item_type == "attachment":
            return hashlib.md5(self._attachment_content(item)).hexdigest()
        return _content_checksum(_canonicalize_taxonomy_record(self._records.get(item.dest_path, {})))

    def read_metadata(self, item: MigrationItem) -> dict | None:
        """Comparable attributes of the source item (for the post-run metadata diff)."""
        source_item = self._items.get(item.dest_path)
        if source_item is None:
            return None
        properties = source_item.properties
        return {
            "created": iso_or_none(properties.get("Created")),
            "modified": iso_or_none(properties.get("Modified")),
        }

    def read_authorship(self, item: MigrationItem) -> tuple[str | None, str | None]:
        """The source author/editor login names (for the authorship diff)."""
        return (
            item.author.login_name if item.author else None,
            item.editor.login_name if item.editor else None,
        )

    def _normalize_name(self, name: str) -> str:
        """Canonicalize a principal name (default groups -> ``default:<Kind>``)."""
        context = getattr(self._list, "context", None)
        web = getattr(context, "web", None) if context is not None else None
        if web is None:
            return name
        if self._default_groups is None:
            self._default_groups = _DefaultGroups(web)
        return self._default_groups.normalize(name)

    def read_permissions(self, item: MigrationItem) -> list[PermissionEntry]:
        """Read the item's *unique* role assignments (best-effort ACL preservation).

        Inherited items return ``[]`` — REST would otherwise report the parent's
        ACL, and copying it would break inheritance on every item.
        """
        source_item = self._items.get(item.dest_path)
        if source_item is None or not _has_unique_role_assignments(source_item):
            return []
        return _read_role_assignments(source_item, resolve=self._principal_for, normalize=self._normalize_name)

    def _principal_for(self, user_id: Any) -> "Principal | None":
        """Resolve a site-user id to a :class:`Principal` (login + PUID), cached."""
        key = parse_int(user_id)
        if key is None:
            return None
        if key in self._users:
            return self._users[key]
        principal: "Principal | None" = None
        try:
            user = self._list.context.web.site_users.get_by_id(cast("str", key)).get().execute_query()
            user_id_info = user.properties.get("UserId")
            system_id = normalize_puid(getattr(user_id_info, "NameId", None))
            principal = Principal(
                login_name=user.login_name or "",
                system_id=system_id,
                display_name=user.title,
                email=user.properties.get("Email"),
            )
        except Exception as e:  # noqa: BLE001 — a missing user degrades to no authorship
            self.warnings.append(f"user {key} could not be resolved: {e}")
        self._users[key] = principal
        return principal

    def close(self) -> None:
        pass


class SharePointListTarget:
    """Imports record payloads into a SharePoint list.

    Pass ``key`` (one or more natural-key columns) to make the target idempotent:
    a hash of those columns is stored in ``key_field`` and each payload is created
    or (``on_conflict="update"``) updated, so re-runs never duplicate. Without a
    key, records are appended and idempotency relies on the checkpoint/manifest.

    ``on_conflict`` may be passed explicitly; otherwise it is derived from
    ``MigrationOptions.conflict_resolution`` by :meth:`configure` (the runner calls
    it before writes): ``OVERWRITE`` → ``"update"``, anything else → ``"skip"``.

    Every migrated item also gets a source-id marker (``identity_field``, default
    ``MigrationSourceId``): the default ``SKIP`` policy then recognizes items already
    on the target (so re-runs do not duplicate) and :meth:`list_paths` pairs source
    and target items for verification. Pass ``identity_field=None`` to opt out.
    List-item attachments are written after their parent records are flushed.

    Pass ``content_type_map`` (a :class:`~office365.migration.map.ContentTypeMap`)
    when the target list's content types were recreated with fresh identifiers:
    every record's ``ContentTypeId`` is rewritten to the target id so items land
    under the recreated content type instead of the wrong (or a missing) one.
    """

    # Marks this target as accepting list-item attachments as extra items (see DataTarget).
    supports_attachments = True

    # Marks this target as remapping Lookup values across migrated lists and Person
    # values by login (see ``_remap_typed_values``).
    supports_typed_values = True

    # Marks this target as replaying a list item's approval state (``_ModerationStatus``
    # and its comments) in the metadata write, which a system update would otherwise
    # reset. Check-out and draft-version state are still not carried.
    supports_item_state = True

    #: The single-item :meth:`write` only queues a create; a chunk must be flushed
    #: before it is durable. The runner therefore routes this target through the
    #: chunked path even at ``concurrency == 1``, so checkpoints never record
    #: ``DONE`` ahead of the actual write.
    deferred_writes = True

    def rebind(self) -> "SharePointListTarget":
        """This target on its own cloned context (see :meth:`SharePointListSource.rebind`)."""
        return SharePointListTarget(
            _cloned_list(self._list),
            key=list(self._key_columns) or None,
            key_field=self._key_field,
            on_conflict=self._on_conflict_override,
            identity_field=self._identity_field,
            content_type_map=self._content_type_map,
        )

    def __init__(
        self,
        target_list: "SPList",
        key: str | list[str] | None = None,
        key_field: str = "MigrationKey",
        on_conflict: str | None = None,
        identity_field: str | None = DEFAULT_LIST_IDENTITY_FIELD,
        content_type_map: "ContentTypeMap | None" = None,
    ) -> None:
        self._list = target_list
        self._key_columns = [key] if isinstance(key, str) else (list(key) if key else [])
        self._key_field = key_field
        self._on_conflict_override = on_conflict
        self._on_conflict = on_conflict or "skip"
        self._target = None
        self._existing: dict = {}
        self._identity_field = identity_field
        self._identity_ensured = False
        self._identity_index: dict | None = None
        self._identity_index_stale = False
        self._identity_index_max_id = 0
        self._attachment_path_cache: set[str] | None = None
        self._content_type_map = content_type_map
        self._login_cache: dict[int, str | None] = {}
        # Author/Editor values already written by ``apply_authorship`` but pending a
        # shared final write (see ``apply_timestamps``); avoids the ValidateUpdateListItem
        # call that restores timestamps silently resetting ``Editor`` to the caller.
        self._pending_authorship: dict[str, dict] = {}
        # Approval state read from the payload, replayed in the metadata write (a
        # system update approves the item); same pending-then-pop lifecycle as above.
        self._pending_approval: dict[str, dict[str, str]] = {}
        self.warnings: list[str] = []
        self._principals_cache: _TargetPrincipals | None = None
        # Lookup and Person columns carry an id that is only meaningful on the
        # source (list-local item id / site-user id). The target remaps each to its
        # own value on write and back to the source value on verification.
        self._columns_cache: _TypedColumns | None = None
        self._lookup_indexes: dict[str, tuple[dict[int, int], dict[int, int]]] = {}
        self._unresolved_lookups: set[tuple[str, int]] = set()
        self._unresolved_users: set[tuple[str, str]] = set()
        self._user_logins: dict[int, str] | None = None

    @property
    def on_conflict(self) -> str:
        """The active record conflict policy (``"skip"`` or ``"update"``)."""
        return self._on_conflict

    def configure(self, options) -> None:
        """Derive ``on_conflict`` from ``MigrationOptions.conflict_resolution``.

        Called by :class:`MigrationRunner` before the run, so a single
        ``conflict_resolution`` drives both file and record targets. An
        ``on_conflict`` passed to the constructor is honored as-is.
        """
        if self._on_conflict_override is None:
            self._on_conflict = conflict_to_on_conflict(options.conflict_resolution)

    def label(self) -> str:
        return f"list:{self._list.title}"

    def exists(self, item: MigrationItem) -> bool:
        # With the identity marker, both records and attachments are recognized on a
        # re-run, so the default ``SKIP`` policy is genuinely idempotent. Without it
        # (``identity_field=None``) nothing is recognized and records append.
        if not self._identity_field:
            return False
        self._ensure_identity()
        if not self._identity_field:
            return False
        if item.item_type == "attachment":
            return str(item.dest_path) in set(self._attachment_paths())
        return self._find_by_identity(item.dest_path) is not None

    def write(self, item: MigrationItem, payload: object) -> None:
        if item.item_type == "attachment":
            self._write_attachment(item, payload)
            return
        self._queue([self._record_for(item, payload)])

    def write_many(
        self,
        items: list[MigrationItem],
        payloads: list[object],
        concurrency: int = 1,
    ) -> list[Failure]:
        """Queue a chunk and flush it immediately, then discard the entities.

        Flushing per chunk (instead of only at :meth:`commit`) keeps a large list
        migration memory-bounded — the queued creates never accumulate for the
        whole run. Attachments in the chunk are written after its records are
        flushed, so their parent items already exist.

        Returns:
            No failures (a batch failure raises; there are no partial successes).
        """
        records: list[dict] = []
        attachments: list[tuple[MigrationItem, object]] = []
        for item, payload in zip(items, payloads):
            if item.item_type == "attachment":
                attachments.append((item, payload))
            else:
                records.append(self._record_for(item, payload))
        if records:
            self._queue(records)
            self._flush(len(records), concurrency)
        for item, payload in attachments:
            self._write_attachment(item, payload)
        return []

    def _record_for(self, item: MigrationItem, payload: object) -> dict:
        """The payload with the target content-type id and source-id marker applied."""
        record = dict(cast(dict, payload))
        if self._content_type_map:
            content_type_id = record.get("ContentTypeId")
            record["ContentTypeId"] = self._content_type_map.resolve(content_type_id)
        if self._identity_field:
            record[self._identity_field] = item.dest_path
        approval = {
            field_name: str(record[record_key])
            for record_key, field_name in _APPROVAL_FIELDS.items()
            if record.get(record_key) is not None
        }
        if approval:
            self._pending_approval[item.dest_path] = approval
        return record

    def translate_record(self, record: dict) -> dict:
        """A source record mapped onto this list without writing it.

        A document library folder is a list item that already exists on the target,
        so its column values cannot go through the create queue: the record is mapped
        here (target content-type id, Lookup ids, Person logins, multi-value shapes)
        and applied with an update instead.
        """
        mapped = dict(record)
        if self._content_type_map:
            resolved = self._content_type_map.resolve(mapped.get("ContentTypeId"))
            if resolved:
                mapped["ContentTypeId"] = resolved
            else:
                mapped.pop("ContentTypeId", None)
        self._remap_typed_values([mapped])
        return mapped

    def _queue(self, records: list[dict]) -> None:
        self._ensure_identity()
        self._remap_typed_values(records)
        if not self._key_columns:
            for record in records:
                self._list.items.queue_records([self._multi_value_create(record)])
            return
        from office365.runtime.converters.upsert import keyed_queue
        from office365.sharepoint.fields.name import internal_field_name

        target = self._target
        if target is None:
            target = self._list.items.upsert_target(key_field=self._key_field)
            target.ensure_key_field()
            self._list.context.execute_query()
            self._existing.update(target.load_keys())
            self._target = target
        key_columns = [internal_field_name(c) for c in self._key_columns]
        keyed_queue(
            _MultiValueCreateTarget(target, self._multi_value_create),
            records,
            key_columns=key_columns,
            existing=self._existing,
            on_conflict=self._on_conflict,
        )

    def _multi_id_keys(self) -> set[str]:
        """The ``...Id`` record keys of the multi-value Lookup/Person columns."""
        names = (*self._multi_lookup_columns(), *self._multi_user_columns())
        return {f"{name}Id" for name in names}

    def _multi_value_create(self, record: dict) -> dict:
        """Reshape multi-value columns for a *create* (``{"results": [...]}``).

        A bare list is the semantic value the source records and the checksum work
        with, and it is also what a MERGE update wants; only a create needs the
        ``{"results": [...]}`` wrapper (live-probed). Lists without multi-value
        columns are passed through untouched.
        """
        keys = self._multi_id_keys() | self._multi_choice_columns()
        if not keys:
            return record
        wrapped = dict(record)
        for key in keys:
            values = _multi_values(wrapped.get(key))
            if values is not None:
                wrapped[key] = _collection_payload(values)
        return wrapped

    def _ensure_identity(self) -> None:
        """Create the source-id marker column (once), best-effort."""
        if self._identity_ensured or not self._identity_field:
            return
        self._identity_ensured = True
        name = self._identity_field
        from office365.sharepoint.fields.creation_information import FieldCreationInformation
        from office365.sharepoint.fields.type import FieldType

        try:
            self._list.fields.ensure(FieldCreationInformation(name, FieldType.Text)).execute_query()
        except Exception as e:  # noqa: BLE001 — identity is best-effort; content still migrates
            self._identity_field = None
            self.warnings.append(f"could not create the {name!r} identity column: {e}")

    def _columns(self) -> _TypedColumns:
        """The target's typed columns.

        Returns ``(lookup: name -> referenced list id, user names, multi-lookup:
        name -> referenced list id, multi-user names, taxonomy: name -> (allows
        many, hidden note field internal name), multi-choice names)``.
        """
        if self._columns_cache is None:
            self._columns_cache = self._load_columns()
        return self._columns_cache

    def _lookup_columns(self) -> dict[str, str]:
        return self._columns()[0]

    def _user_columns(self) -> set[str]:
        return self._columns()[1]

    def _multi_lookup_columns(self) -> dict[str, str]:
        return self._columns()[2]

    def _multi_user_columns(self) -> set[str]:
        return self._columns()[3]

    def _taxonomy_columns(self) -> dict[str, tuple[bool, str | None]]:
        return self._columns()[4]

    def _multi_choice_columns(self) -> set[str]:
        return self._columns()[5]

    def _load_columns(self) -> _TypedColumns:
        lookups: dict[str, str] = {}
        users: set[str] = set()
        multi_lookups: dict[str, str] = {}
        multi_users: set[str] = set()
        taxonomy: dict[str, tuple[bool, str | None]] = {}
        multi_choices: set[str] = set()
        try:
            fields = (
                self._list.fields.select(
                    ["InternalName", "TypeAsString", "LookupList", "Id", "TextField", "AllowMultipleValues"]
                )
                .get()
                .execute_query()
            )
        except Exception as e:  # noqa: BLE001 — without columns we cannot remap; content still migrates
            self.warnings.append(f"could not read target columns for typed-value remapping: {e}")
            return lookups, users, multi_lookups, multi_users, taxonomy, multi_choices
        by_id = {normalize_guid(getattr(field, "id", None)): getattr(field, "internal_name", None) for field in fields}
        for field in fields:
            internal_name = getattr(field, "internal_name", None)
            if not internal_name or internal_name in _PERSON_EXCLUDED:
                continue
            field_type = getattr(field, "type_as_string", None)
            if field_type in _TAXONOMY_FIELD_TYPES:
                # The companion note column that actually carries the write payload
                # has an unpredictable name; resolve it through the column's
                # ``TextField`` id.
                note_name = by_id.get(normalize_guid(field.properties.get("TextField")))
                taxonomy[internal_name] = (field_type == "TaxonomyFieldTypeMulti", note_name)
            elif field_type in _TYPED_VALUE_TYPES:
                multiple = _allows_multiple_values(field)
                if field_type.startswith("User"):
                    if multiple:
                        multi_users.add(internal_name)
                    else:
                        users.add(internal_name)
                else:
                    list_id = normalize_guid(field.properties.get("LookupList"))
                    if not list_id:
                        continue
                    if multiple:
                        multi_lookups[internal_name] = list_id
                    else:
                        lookups[internal_name] = list_id
            elif _is_multi_choice_column(field):
                multi_choices.add(internal_name)
        return lookups, users, multi_lookups, multi_users, taxonomy, multi_choices

    def _lookup_index(self, target_list_id: str) -> tuple[dict[int, int], dict[int, int]]:
        """``(source id -> target id, target id -> source id)`` for a referenced list."""
        cached = self._lookup_indexes.get(target_list_id)
        if cached is not None:
            return cached
        forward: dict[int, int] = {}
        backward: dict[int, int] = {}
        self._flush_pending()
        try:
            referenced = self._list.context.web.lists.get_by_id(target_list_id)
            items = referenced.items.select(["Id", DEFAULT_LIST_IDENTITY_FIELD]).get_all().execute_query()
        except Exception as e:  # noqa: BLE001 — an unreadable referenced list is reported, not fatal
            self.warnings.append(f"lookup target list {target_list_id} could not be read: {e}")
            items = []
        for referenced_item in items:
            source_id = parse_int(referenced_item.properties.get(DEFAULT_LIST_IDENTITY_FIELD))
            target_id = parse_int(referenced_item.id)
            if source_id is None or target_id is None:
                continue
            forward[source_id] = target_id
            backward[target_id] = source_id
        self._lookup_indexes[target_list_id] = (forward, backward)
        return forward, backward

    def _remap_typed_values(self, records: list[dict]) -> None:
        """Translate each record's source lookup/person ids into target values.

        A lookup references another migrated list (matched on its items' source-id
        marker); a person carries the *login name* the source annotated, resolved
        here with ``EnsureUser``. Either value with no match is dropped and reported
        once rather than written as a wrong id.
        """
        self._remap_lookups(records)
        self._remap_users(records)
        self._remap_multi_lookups(records)
        self._remap_multi_users(records)
        self._remap_taxonomies(records)

    def _remap_lookups(self, records: list[dict]) -> None:
        columns = self._lookup_columns()
        if not columns:
            return
        for record in records:
            for internal_name, target_list_id in columns.items():
                key = f"{internal_name}Id"
                source_id = parse_int(record.get(key))
                if source_id is None:
                    continue
                forward, _ = self._lookup_index(target_list_id)
                target_id = forward.get(source_id)
                if target_id is None:
                    record.pop(key, None)
                    self._report_unresolved_lookup(internal_name, source_id)
                    continue
                record[key] = target_id

    def _remap_users(self, records: list[dict]) -> None:
        columns = self._user_columns()
        if not columns:
            return
        for record in records:
            for internal_name in columns:
                key = f"{internal_name}Id"
                login = record.get(key)
                if not isinstance(login, str) or not login:
                    continue
                user = self._principals().user(login)
                if user is None or getattr(user, "id", None) is None:
                    record.pop(key, None)
                    self._report_unresolved_user(internal_name, login)
                    continue
                record[key] = user.id

    def _remap_multi_lookups(self, records: list[dict]) -> None:
        columns = self._multi_lookup_columns()
        if not columns:
            return
        for record in records:
            for internal_name, target_list_id in columns.items():
                key = f"{internal_name}Id"
                source_ids = _id_list(record.get(key))
                if not source_ids:
                    continue
                forward, _ = self._lookup_index(target_list_id)
                target_ids: list[int] = []
                for value in source_ids:
                    source_id = parse_int(value)
                    target_id = forward.get(source_id) if source_id is not None else None
                    if target_id is None:
                        if source_id is not None:
                            self._report_unresolved_lookup(internal_name, source_id)
                        continue
                    target_ids.append(target_id)
                if target_ids:
                    record[key] = target_ids
                else:
                    record.pop(key, None)

    def _remap_multi_users(self, records: list[dict]) -> None:
        columns = self._multi_user_columns()
        if not columns:
            return
        for record in records:
            for internal_name in columns:
                key = f"{internal_name}Id"
                logins = record.get(key)
                if not isinstance(logins, (list, tuple)) or not logins:
                    continue
                target_ids: list[int] = []
                for login in logins:
                    user = self._principals().user(login) if isinstance(login, str) and login else None
                    user_id = getattr(user, "id", None)
                    if user is None or user_id is None:
                        self._report_unresolved_user(internal_name, str(login))
                        continue
                    target_ids.append(user_id)
                if target_ids:
                    record[key] = target_ids
                else:
                    record.pop(key, None)

    def _remap_taxonomies(self, records: list[dict]) -> None:
        """Write taxonomy terms in the form SharePoint accepts on the target.

        A single-value column takes a typed ``SP.Taxonomy.TaxonomyFieldValue``
        object; a multi-value column only accepts the hidden note companion's text
        form ``-1;#Label|guid;#...`` (typed-collection JSON is rejected server-side).
        The term id is authoritative — the label can be left blank. A column with no
        target counterpart is dropped and reported rather than sent as an unknown
        property.
        """
        columns = self._taxonomy_columns()
        unresolved: set[str] = set()
        for record in records:
            for internal_name, value in list(record.items()):
                if not _is_taxonomy_value(value):
                    continue
                guids = _taxonomy_guids(value)
                column = columns.get(internal_name)
                if column is None:
                    record.pop(internal_name, None)
                    unresolved.add(internal_name)
                    continue
                allow_many, note_name = column
                if not guids:
                    record.pop(internal_name, None)
                    continue
                if allow_many and note_name:
                    record.pop(internal_name, None)
                    record[note_name] = ";#".join(f"-1;#|{guid}" for guid in guids)
                elif allow_many:
                    record.pop(internal_name, None)
                    unresolved.add(internal_name)
                else:
                    record[internal_name] = {
                        "__metadata": {"type": "SP.Taxonomy.TaxonomyFieldValue"},
                        "Label": "",
                        "TermGuid": guids[0],
                        "WssId": -1,
                    }
        if unresolved:
            self.warnings.append(
                f"taxonomy column(s) not available on the target, values left empty: {', '.join(sorted(unresolved))}"
            )

    def _report_unresolved_user(self, internal_name: str, login: str) -> None:
        marker = (internal_name, login)
        if marker in self._unresolved_users:
            return
        self._unresolved_users.add(marker)
        self.warnings.append(
            f"person column '{internal_name}' login {login!r} could not be resolved on the target; "
            "the value was left empty"
        )

    def _target_user_logins(self) -> dict[int, str]:
        """The target web's ``{site-user id: login name}`` map (cached)."""
        if self._user_logins is None:
            mapping: dict[int, str] = {}
            try:
                for site_user in self._list.context.web.site_users.get().execute_query():
                    user_id = parse_int(site_user.id)
                    if user_id is not None and site_user.login_name:
                        mapping[user_id] = site_user.login_name
            except Exception as e:  # noqa: BLE001 — without the map persons are left as ids
                self.warnings.append(f"could not read target site users for person verification: {e}")
            self._user_logins = mapping
        return self._user_logins

    def _report_unresolved_lookup(self, internal_name: str, source_id: int) -> None:
        marker = (internal_name, source_id)
        if marker in self._unresolved_lookups:
            return
        self._unresolved_lookups.add(marker)
        self.warnings.append(
            f"lookup column '{internal_name}' value {source_id} could not be mapped to a target item "
            "(the referenced list's items were not migrated first); the value was left empty"
        )

    def _canonicalize_lookups(self, properties: dict) -> None:
        """Rewrite target lookup ids back to the source ids (symmetric to the write).

        The source checksum holds the source item id; the target's fresh item holds
        the target id. Mapping the latter back lets the content spot-check compare
        the two like for like instead of reporting a false mismatch.
        """
        for internal_name, target_list_id in self._lookup_columns().items():
            key = f"{internal_name}Id"
            target_id = parse_int(properties.get(key))
            if target_id is None:
                continue
            _, backward = self._lookup_index(target_list_id)
            source_id = backward.get(target_id)
            if source_id is not None:
                properties[key] = source_id
        for internal_name, target_list_id in self._multi_lookup_columns().items():
            key = f"{internal_name}Id"
            target_ids = _id_list(properties.get(key))
            if not target_ids:
                continue
            _, backward = self._lookup_index(target_list_id)
            mapped: list[Any] = []
            for value in target_ids:
                target_id = parse_int(value)
                mapped.append(backward.get(target_id, value) if target_id is not None else value)
            properties[key] = mapped

    def _canonicalize_users(self, properties: dict) -> None:
        """Rewrite target person ids back to the login names the source recorded."""
        columns = self._user_columns()
        logins = self._target_user_logins() if columns or self._multi_user_columns() else {}
        for internal_name in columns:
            key = f"{internal_name}Id"
            user_id = parse_int(properties.get(key))
            if user_id is None:
                continue
            login = logins.get(user_id)
            if login is not None:
                properties[key] = login
        for internal_name in self._multi_user_columns():
            key = f"{internal_name}Id"
            user_ids = _id_list(properties.get(key))
            if not user_ids:
                continue
            mapped_logins: list[Any] = []
            for value in user_ids:
                user_id = parse_int(value)
                mapped_logins.append(logins.get(user_id, value) if user_id is not None else value)
            properties[key] = mapped_logins

    def _canonicalize_multi_choices(self, properties: dict) -> None:
        """Reduce a read-back multi-choice cell to the bare list the source records.

        A live read returns the selected values as a positional mapping
        (``{0: "red", 1: "green"}``); the source checksum holds a bare list, so the
        two are only comparable after the same projection.
        """
        for internal_name in self._multi_choice_columns():
            if internal_name not in properties:
                continue
            values = _multi_values(properties.get(internal_name))
            if values:
                properties[internal_name] = values
            else:
                properties.pop(internal_name, None)

    def _write_attachment(self, item: MigrationItem, payload: object) -> None:
        if not self._identity_field:
            raise NotImplementedError("attachments need the identity column, which could not be created")
        parent_id, _, filename = str(item.dest_path).partition("/")
        if not filename:
            raise ValueError(f"invalid attachment destination {item.dest_path!r}")
        self._flush_pending()
        parent = self._find_by_identity(parent_id)
        if parent is None:
            raise ValueError(f"no target item for source id {parent_id!r}; cannot attach {filename!r}")
        content = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
        parent.attachment_files.add({"filename": filename, "content": content}).execute_query()
        if self._attachment_path_cache is not None:
            self._attachment_path_cache.add(str(item.dest_path))

    def _flush_pending(self) -> None:
        if self._list.context.has_pending_request:
            self._flush(DEFAULT_BATCH_SIZE, 1)

    def _find_by_identity(self, source_id: str):
        if self._identity_index is None or self._identity_index_stale:
            self._refresh_identity_index()
        return self._identity_index.get(str(source_id)) if self._identity_index else None

    def _refresh_identity_index(self) -> None:
        """Load, or incrementally extend, the source-id -> target item map.

        After a chunk is flushed only the newly created items are re-read
        (``Id gt <max>``) instead of re-scanning the whole list, so refreshing the
        index per chunk stays linear rather than O(n²).
        """
        if not self._identity_field:
            self._identity_index = {}
            return
        if self._identity_index is not None and self._identity_index_max_id > 0:
            self._index_identity_items(self._query_identity_items(f"Id gt {self._identity_index_max_id}"))
            return
        self._identity_index = {}
        self._identity_index_max_id = 0
        self._index_identity_items(self._query_identity_items())

    def _query_identity_items(self, filter_expr: str | None = None):
        # A read query would implicitly flush any queued writes on this context;
        # flush them explicitly first so the cached index stays consistent.
        self._flush_pending()
        columns = ["Id", self._identity_field, "Created", "Modified", "AuthorId", "EditorId"]
        query = self._list.items.select(columns)
        if filter_expr:
            query = query.filter(filter_expr)
        return query.get_all().execute_query()

    def _index_identity_items(self, items) -> None:
        if self._identity_index is None:
            self._identity_index = {}
        for target_item in items:
            value = target_item.properties.get(self._identity_field)
            if value is None:
                continue
            self._identity_index[str(value)] = target_item
            item_id = parse_int(getattr(target_item, "id", None))
            if item_id is not None and item_id > self._identity_index_max_id:
                self._identity_index_max_id = item_id
        self._identity_index_stale = False

    def _attachment_paths(self) -> list[str]:
        if not self._identity_field:
            return []
        if self._attachment_path_cache is None:
            self._attachment_path_cache = set(self._query_attachment_paths())
        return list(self._attachment_path_cache)

    def _query_attachment_paths(self) -> list[str]:
        if not self._identity_field:
            return []
        self._flush_pending()
        items = (
            self._list.items.select(["Id", self._identity_field]).expand(["AttachmentFiles"]).get_all().execute_query()
        )
        paths: list[str] = []
        for target_item in items:
            value = target_item.properties.get(self._identity_field)
            if value is None:
                continue
            for attachment in target_item.properties.get("AttachmentFiles") or []:
                name = getattr(attachment, "file_name", None)
                if name:
                    paths.append(f"{value}/{name}")
        return paths

    def list_paths(self) -> list[str]:
        if not self._identity_field:
            return [str(i.id) for i in self._list.items.get().execute_query()]
        # An empty source list never queues a write, so the marker column was not
        # created during migration; ensure it before verification queries it.
        self._ensure_identity()
        if not self._identity_field:
            return [str(i.id) for i in self._list.items.get().execute_query()]
        if self._identity_index is None or self._identity_index_stale:
            self._refresh_identity_index()
        index = self._identity_index or {}
        return list(index.keys()) + self._attachment_paths()

    def checksum(self, item: MigrationItem) -> str:
        if item.item_type == "attachment":
            return self._attachment_checksum(item)
        target_item = self._fresh_target_item(item)
        if target_item is None:
            return ""
        return self.content_checksum(dict(target_item.properties))

    def content_checksum(self, properties: dict) -> str:
        """The comparable content hash of an item's read-back properties.

        Used for both a written record and a folder's item, so a library folder's
        column values can be reconciled against the source record that produced them.
        """
        properties = _canonicalize_taxonomy_record(dict(properties))
        self._canonicalize_lookups(properties)
        self._canonicalize_users(properties)
        self._canonicalize_multi_choices(properties)
        extra = {self._identity_field} if self._identity_field else set()
        # The hidden taxonomy note companion is not part of the source's portable
        # content; it is verified through the term ids on the column itself.
        extra.update(note for _, note in self._taxonomy_columns().values() if note)
        # The target derives its own ``<name>StringId`` companion; it is not part of
        # the source's canonical content.
        extra.update(f"{name}StringId" for name in self._user_columns())
        extra.update(f"{name}StringId" for name in self._multi_user_columns())
        return _content_checksum(properties, frozenset(extra))

    def _attachment_checksum(self, item: MigrationItem) -> str:
        parent_id, _, filename = str(item.dest_path).partition("/")
        parent = self._find_by_identity(parent_id)
        if parent is None:
            return ""
        try:
            data = parent.attachment_files.get_by_filename(filename).get_content().execute_query().value
        except Exception:  # noqa: BLE001 — a missing/unreadable attachment is unverifiable
            return ""
        return hashlib.md5(data).hexdigest() if data else ""

    def commit(self, options=None) -> None:
        """Flush any remaining queued record writes through an OData batch."""
        batch_size = getattr(options, "batch_size", None) or DEFAULT_BATCH_SIZE
        concurrency = getattr(options, "concurrency", None) or 1
        self._flush(batch_size, concurrency)
        self._pending_authorship.clear()
        self._pending_approval.clear()

    def _flush(self, batch_size: int, concurrency: int) -> None:
        if not self._list.context.has_pending_request:
            return
        self._list.context.execute_batch(items_per_batch=batch_size, concurrency=concurrency)
        self._list.items.clear()
        # Records were just created/updated, so the cached source-id index needs an
        # incremental refresh (new items only) before the next lookup.
        if self._identity_index is not None:
            self._identity_index_stale = True

    def _principals(self) -> _TargetPrincipals:
        """The (lazily built) target principal/role resolver."""
        if self._principals_cache is None:
            self._principals_cache = _TargetPrincipals(self._list.context.web, self.warnings)
        return self._principals_cache

    def _target_item(self, item: MigrationItem):
        """The written target item for a record (``None`` for attachments/folders)."""
        if item.item_type == "attachment":
            return None
        return self._find_by_identity(item.dest_path)

    def apply_timestamps(self, item: MigrationItem) -> None:
        """Best-effort: restore ``Created``/``Modified`` on the written item.

        Uses ``ValidateUpdateListItem`` with ``bNewDocumentUpdate=True`` -- a
        system update (the CSOM ``UpdateOverwriteVersion`` path), so the metadata
        lands **without** creating a new version and a migrated record keeps its
        original version instead of accumulating one version per fidelity write.
        ``datesInUTC=True`` requires the ``...Z`` UTC form. Authorship values
        resolved for the same item are folded into this final write so both land
        atomically, in one system update.
        """
        target_item = self._target_item(item)
        if target_item is None:
            return
        form_values: dict = {}
        created = _sp_utc_timestamp(item.created)
        modified = _sp_utc_timestamp(item.modified)
        if created:
            form_values["Created"] = created
        if modified:
            form_values["Modified"] = modified
        form_values.update(self._pending_authorship.pop(item.dest_path, {}))
        form_values.update(self._pending_approval.pop(item.dest_path, {}))
        if form_values:
            result = target_item.validate_update_list_item(
                form_values, dates_in_utc=True, new_document_update=True
            ).execute_query()
            _report_rejected_fields(result, self.warnings, f"timestamps {item.dest_path}")

    def apply_authorship(self, item: MigrationItem) -> None:
        """Best-effort: resolve ``Author``/``Editor`` and cache them for one write.

        A principal is applied only when its login name resolves to a target user
        (``EnsureUser``); unresolved principals are skipped (same-tenant only).

        Nothing is sent here. ``ValidateUpdateListItem`` is one request per call, so
        writing the resolved principals immediately and then again with the
        timestamps cost every preserved item two system updates. The values are
        cached and folded into the timestamps write, or written by
        :meth:`finalize_fidelity` when timestamps are not preserved.
        """
        target_item = self._target_item(item)
        if target_item is None:
            return
        author = self._principals().user(item.author.login_name if item.author else None)
        editor = self._principals().user(item.editor.login_name if item.editor else None)
        if author is not None and _is_system_principal(author):
            author = None
        if editor is not None and _is_system_principal(editor):
            editor = None
        if author is None and editor is None and not self._pending_approval.get(item.dest_path):
            return
        form_values: dict = {}
        if author is not None:
            form_values["Author"] = FieldUserValue(author.id, author.login_name)
        if editor is not None:
            form_values["Editor"] = FieldUserValue(editor.id, editor.login_name)
        # Replay the approval state here too: this write is itself a system update, so
        # on a run that restores authorship without timestamps it is the last one.
        form_values.update(self._pending_approval.get(item.dest_path, {}))
        self._pending_authorship[item.dest_path] = dict(form_values)

    def finalize_fidelity(self, item: MigrationItem) -> None:
        """Write the fidelity values that were only cached for this item.

        The last hook wins the write: with timestamps preserved that is
        :meth:`apply_timestamps`; without them it is this method, so the item still
        gets one system update instead of one per property group. It runs before
        the approval write, which has to stay last (a system update re-approves).
        """
        form_values = self._pending_authorship.pop(item.dest_path, {})
        form_values.update(self._pending_approval.pop(item.dest_path, {}))
        if not form_values:
            return
        target_item = self._target_item(item)
        if target_item is None:
            return
        result = target_item.validate_update_list_item(
            form_values, dates_in_utc=True, new_document_update=True
        ).execute_query()
        _report_rejected_fields(result, self.warnings, f"authorship {item.dest_path}")

    def apply_permissions(self, item: MigrationItem, permissions: list[PermissionEntry]) -> None:
        """Best-effort: replay the source item's unique ACLs onto the target item.

        Same-tenant only — cross-tenant identity mapping is out of scope. See
        :func:`_replay_role_assignments` for what happens to principals, roles and
        inheritance that cannot be resolved.
        """
        target_item = self._target_item(item)
        if target_item is None:
            return
        _replay_role_assignments(target_item, self._principals(), permissions, self.warnings, item.dest_path)
        self._list.context.execute_query()

    def _fresh_target_item(self, item: MigrationItem):
        """The written target item with freshly-read properties (verification hooks).

        The cached identity-index object predates the fidelity writes
        (``apply_timestamps``/``apply_authorship``), so re-read it before diffing.
        """
        target_item = self._target_item(item)
        if target_item is not None:
            target_item.get().execute_query()
        return target_item

    def read_metadata(self, item: MigrationItem) -> dict | None:
        """Comparable attributes of the written item (for the metadata diff)."""
        target_item = self._fresh_target_item(item)
        if target_item is None:
            return None
        properties = target_item.properties
        return {
            "created": iso_or_none(properties.get("Created")),
            "modified": iso_or_none(properties.get("Modified")),
        }

    def read_authorship(self, item: MigrationItem) -> tuple[str | None, str | None]:
        """The written item's author/editor login names (for the authorship diff)."""
        target_item = self._fresh_target_item(item)
        if target_item is None:
            return (None, None)
        properties = target_item.properties
        return (
            _user_login(self._list.context.web, properties.get("AuthorId"), self._login_cache),
            _user_login(self._list.context.web, properties.get("EditorId"), self._login_cache),
        )

    def read_permissions(self, item: MigrationItem) -> list[PermissionEntry]:
        """Read the written item's *unique* role assignments (for the permission diff)."""
        target_item = self._fresh_target_item(item)
        if target_item is None or not _has_unique_role_assignments(target_item, refresh=True):
            return []
        return _read_role_assignments(target_item, normalize=self._principals().normalize)

    def close(self) -> None:
        pass


class SharePointLibrarySource:
    """Enumerates a document library's files and folders (recursively) for migration.

    Folder entries (``item_type="folder"``, trailing ``/`` on the destination)
    preserve the folder structure — including **empty** folders — on the target, and
    carry the folder's own column values (a document set's metadata, a managed
    folder's department) as their payload when the parent list is known.
    """

    def rebind(self) -> "SharePointLibrarySource":
        """This source on its own cloned context (see :meth:`SharePointListSource.rebind`)."""
        context = _cloned_context(self._folder)
        sp_list = _cloned_list(self._sp_list, context) if self._sp_list is not None else None
        return SharePointLibrarySource(_cloned_folder(self._folder, context), self.on_bytes, sp_list=sp_list)

    def __init__(
        self,
        library_folder: "Folder",
        on_bytes: Callable[[int, int | None], None] | None = None,
        sp_list: "SPList | None" = None,
    ) -> None:
        self._folder = library_folder
        # The parent list, when known — author/editor ids (``AuthorId``/``EditorId``)
        # are not exposed on the ``File`` resource and must be read from its items.
        self._sp_list = sp_list
        # Folder column values come from the list's items and are projected exactly
        # like a record's (typed values normalized), so that code is reused here.
        self._list_source = SharePointListSource(sp_list) if sp_list is not None else None
        self._folder_payloads: dict[str, dict] | None = None
        self._files: dict[str, "File"] = {}
        # Folder resources by library-relative path, so their own system metadata
        # (``TimeCreated``/``TimeLastModified``) can be diffed after the run.
        self._folders: dict[str, "Folder"] = {}
        self._users: dict[int, "Principal | None"] = {}
        self._default_groups: _DefaultGroups | None = None
        self._item_authors: dict[str, tuple[int | None, int | None]] | None = None
        self._item_unique: dict[str, bool] | None = None
        # Content-approval state by file URL, read alongside the author ids (only
        # when the library moderates).
        self._item_moderation: dict[str, dict] | None = None
        # Server-relative URLs of checked-out files, read alongside the author ids.
        self._item_checkout: set[str] | None = None
        self._moderation_on: bool | None = None
        self.warnings: list[str] = []
        # Optional hook invoked while a file downloads: (bytes_read, file_size)
        self.on_bytes = on_bytes

    def label(self) -> str:
        return f"library:{self._folder.server_relative_url}"

    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        # The root folder's URL may not be loaded yet (e.g. via
        # ``list.root_folder``); fetch it so destinations stay library-relative
        # instead of carrying the site/list path prefix.
        root = self._folder.server_relative_url
        if root is None:
            self._folder.ensure_properties(["ServerRelativeUrl"]).execute_query()
            root = self._folder.server_relative_url or ""
        root = root.rstrip("/")
        extra = _site_assets_scaffolding(self._folder)
        loaded_folders = self._folder.get_folders(recursive=True).execute_query()
        loaded = self._folder.get_files(recursive=True).execute_query()
        authors = self._file_authors()

        def _rel(url: str) -> str:
            return url[len(root) :].lstrip("/") if root else url.lstrip("/")

        result: list[MigrationItem] = []
        seen: set[str] = set()
        for folder in loaded_folders:
            url = folder.server_relative_url or ""
            rel = _rel(url)
            if not rel or rel in seen or _is_system_path(rel, extra):
                continue
            seen.add(rel)
            self._folders[rel] = folder
            author_id, editor_id = authors.get(url, (None, None))
            folder_item = MigrationItem(
                source_path=url,
                dest_path=f"{rel}/",
                item_type="folder",
                modified=iso_or_none(folder.time_last_modified),
                created=iso_or_none(folder.time_created),
                author_id=author_id,
                editor_id=editor_id,
            )
            if author_id is not None:
                folder_item.author = self._principal_for(author_id)
            if editor_id is not None:
                folder_item.editor = self._principal_for(editor_id)
            result.append(folder_item)
            emit_progress(progress, done=len(result), stage="planning", items=[folder])
        for file in loaded:
            url = file.server_relative_url or ""
            rel = _rel(url)
            if _is_system_path(rel, extra):
                continue
            self._files[rel] = file
            author_id = parse_int(file.author.id)
            editor_id = parse_int(file.modified_by.id)
            if author_id is None and editor_id is None:
                author_id, editor_id = authors.get(url, (None, None))
            item = MigrationItem(
                source_path=url,
                dest_path=rel,
                size_bytes=file.length or 0,
                item_type="file",
                modified=iso_or_none(file.time_last_modified),
                created=iso_or_none(file.time_created),
                author_id=author_id,
                editor_id=editor_id,
                source_id=str(file.unique_id) if file.unique_id else None,
                version_label=file.ui_version_label,
            )
            if author_id is not None:
                item.author = self._principal_for(author_id)
            if editor_id is not None:
                item.editor = self._principal_for(editor_id)
            result.append(item)
            emit_progress(progress, done=len(result), stage="planning", items=[file])
        self._report_checkouts(result)
        self._report_drafts(result)
        return result

    def _report_checkouts(self, items: list[MigrationItem]) -> None:
        """Warn about files whose in-progress edits REST cannot see.

        A checked-out file exposes its last **checked-in** content, so the copy is
        faithful to what the source returns while the author's pending edits stay
        behind. Verification cannot catch that — it compares the same read — so the
        loss is reported here instead of passing silently.
        """
        checkout = self._item_checkout or set()
        checked = sorted(item.dest_path for item in items if item.item_type != "folder" and item.source_path in checkout)
        if not checked:
            return
        shown = ", ".join(checked[:_WARNING_SAMPLE])
        if len(checked) > _WARNING_SAMPLE:
            shown = f"{shown} and {len(checked) - _WARNING_SAMPLE} more"
        self.warnings.append(
            f"{len(checked)} checked-out file(s) were copied from their last checked-in version "
            f"(in-progress edits are not visible over REST): {shown}"
        )

    def _report_drafts(self, items: list[MigrationItem]) -> None:
        """Warn about files whose current version is an un-published (minor) draft.

        REST returns the *draft* content, so the copy is faithful to the version the
        source reports — but version history is not preserved, so the published
        version a draft supersedes never reaches the target and the copy keeps the
        draft alone. Verification compares the same read and cannot see the
        difference, so the loss is reported here instead of passing silently.

        The signal rides the file listing (``MinorVersion``), so this costs no extra
        request: a published file is ``x.0``, a draft ``x.n`` with ``n > 0``.
        """
        drafts: list[str] = []
        for item in items:
            if item.item_type == "folder":
                continue
            file = self._files.get(item.dest_path)
            if file is None or not file.minor_version:
                continue
            drafts.append(item.dest_path)
        if not drafts:
            return
        drafts.sort()
        shown = ", ".join(drafts[:_WARNING_SAMPLE])
        if len(drafts) > _WARNING_SAMPLE:
            shown = f"{shown} and {len(drafts) - _WARNING_SAMPLE} more"
        self.warnings.append(
            f"{len(drafts)} file(s) are on an un-published (minor) version: the draft content "
            f"is copied, the published version it supersedes is not (version history is not "
            f"preserved): {shown}"
        )

    def read(self, item: MigrationItem) -> object:
        if item.item_type == "folder":
            # A folder's payload is its column values (empty when it carries none).
            return self._folder_values(item) or b""
        file = self._files.get(item.dest_path)
        if file is None:
            raise FileNotFoundError(item.source_path)
        buffer = io.BytesIO()
        total = file.length or 0

        def _chunk_downloaded(bytes_read: int) -> None:
            if self.on_bytes is not None:
                self.on_bytes(bytes_read, total or None)

        file.download_session(buffer, chunk_downloaded=_chunk_downloaded).execute_query()
        return buffer.getvalue()

    def read_version_history(self, item: MigrationItem) -> tuple[str | None, list[tuple[str, bytes]]]:
        """Read the file's current version label and its older versions.

        Returns ``(current_label, older)`` where ``older`` is oldest-first and
        excludes the current version (which :meth:`read` already supplies). The
        current label comes from ``UIVersionLabel``; older content is streamed
        from each ``File.Versions`` entry. Folders have no version history.
        """
        if item.item_type == "folder":
            return None, []
        file = self._files.get(item.dest_path)
        if file is None:
            raise FileNotFoundError(item.source_path)
        if file.ui_version_label is None:
            file.ensure_property("UIVersionLabel").execute_query()
        older: list[tuple[str, bytes]] = []
        for version in file.versions.get().execute_query():
            label = version.version_label
            if not label:
                continue
            data = version.open_binary_stream().execute_query().value
            older.append((label, data or b""))
        older.sort(key=lambda row: _version_sort_key(row[0]))
        return file.ui_version_label, older

    @property
    def supports_folder_records(self) -> bool:
        """Whether a folder's column values are migrated *and* comparable."""
        return self._list_source is not None

    def checksum(self, item: MigrationItem) -> str:
        if item.item_type == "folder":
            return _content_checksum(_canonicalize_taxonomy_record(self._folder_values(item)))
        return hashlib.md5(cast(bytes, self.read(item))).hexdigest()

    def _folder_values(self, item: MigrationItem) -> dict:
        """The source folder's column values (empty when it carries none)."""
        if self._folder_payloads is None:
            payloads: dict[str, dict] = {}
            if self._sp_list is None or self._list_source is None:
                self.warnings.append(
                    "folder column values were not read: the parent library is unknown "
                    "(pass sp_list to SharePointLibrarySource)"
                )
            else:
                payloads.update(self._list_source.folder_records())
                self.warnings.extend(self._list_source.warnings)
            self._folder_payloads = payloads
        return self._folder_payloads.get(str(item.source_path).rstrip("/"), {})

    def read_permissions(self, item: MigrationItem) -> list[PermissionEntry]:
        """Read the item's role assignments (for best-effort ACL preservation).

        Returns one :class:`PermissionEntry` per principal (user or group), keyed
        by login name; empty for items with no unique assignments.
        """
        securable = self._securable(item)
        if securable is None:
            return []
        # Files: reuse the unique-ACL flag read with the authorship pass (the
        # ``File``/``ListItem`` resources do not expose it without an extra GET).
        if item.item_type != "folder" and self._item_unique is not None:
            unique = self._item_unique.get(item.source_path)
            if unique is not None:
                securable.properties["HasUniqueRoleAssignments"] = unique
        if not _has_unique_role_assignments(securable):
            return []
        return _read_role_assignments(securable, resolve=self._principal_for, normalize=self._normalize_name)

    def _normalize_name(self, name: str) -> str:
        """Canonicalize a principal name (default groups -> ``default:<Kind>``)."""
        context = getattr(self._folder, "context", None)
        web = getattr(context, "web", None) if context is not None else None
        if web is None:
            return name
        if self._default_groups is None:
            self._default_groups = _DefaultGroups(web)
        return self._default_groups.normalize(name)

    def read_metadata(self, item: MigrationItem) -> dict | None:
        """Comparable attributes of the source item (for the post-run metadata diff)."""
        if item.item_type == "folder":
            folder = self._folders.get(str(item.dest_path).rstrip("/"))
            if folder is None:
                return None
            return {
                "created": iso_or_none(folder.time_created),
                "modified": iso_or_none(folder.time_last_modified),
            }
        file = self._files.get(item.dest_path)
        if file is None:
            return None
        metadata = {
            "created": iso_or_none(file.time_created),
            "modified": iso_or_none(file.time_last_modified),
            "size_bytes": file.length or 0,
        }
        self._file_authors()
        state = (self._item_moderation or {}).get(item.source_path)
        if state:
            metadata["moderation_status"] = state.get("_ModerationStatus")
        return metadata

    def read_authorship(self, item: MigrationItem) -> tuple[str | None, str | None]:
        """The source author/editor login names (for the authorship diff)."""
        return (
            item.author.login_name if item.author else None,
            item.editor.login_name if item.editor else None,
        )

    def _securable(self, item: MigrationItem):
        if item.item_type == "folder":
            return self._folder.context.web.get_folder_by_server_relative_path(item.source_path).list_item_all_fields
        file = self._files.get(item.dest_path)
        return file.listItemAllFields if file is not None else None

    def _principal_for(self, user_id: Any) -> "Principal | None":
        """Resolve a site-user id to a :class:`Principal` (login + PUID), cached."""
        key = parse_int(user_id)
        if key is None:
            return None
        if key in self._users:
            return self._users[key]
        principal: "Principal | None" = None
        try:
            user = self._folder.context.web.site_users.get_by_id(cast("str", key)).get().execute_query()
            user_id_info = user.properties.get("UserId")
            raw_id = getattr(user_id_info, "NameId", None)
            system_id = normalize_puid(raw_id)
            if raw_id and system_id is None:
                # e.g. the app principal, whose ``UserId.NameId`` is not a PUID.
                # Emitting it would fail the whole ingestion job, so drop it.
                self.warnings.append(
                    f"user {key} ({user.login_name!r}) has no usable PUID ({raw_id!r}); "
                    "it is omitted from the server-side user map"
                )
            principal = Principal(
                login_name=user.login_name or "",
                system_id=system_id,
                display_name=user.title,
                email=user.properties.get("Email"),
            )
        except Exception as e:  # noqa: BLE001 — a missing user degrades to no authorship
            self.warnings.append(f"user {key} could not be resolved: {e}")
        self._users[key] = principal
        return principal

    def _file_authors(self) -> dict[str, tuple[int | None, int | None]]:
        """Author/editor ids by server-relative file URL (one list-items read).

        ``File.Author``/``ModifiedBy`` is a non-expandable navigation on the File
        resource, so the ids come from the parent library's list items.
        """
        if self._item_authors is not None:
            return self._item_authors
        authors: dict[str, tuple[int | None, int | None]] = {}
        unique: dict[str, bool] = {}
        moderation: dict[str, dict] = {}
        checkout: set[str] = set()
        moderates = self._moderation_enabled()
        if self._sp_list is not None:
            try:
                # ``CheckoutUser`` is a user field: it only projects when its
                # sub-properties are selected *and* the field is expanded — a bare
                # ``$select=CheckoutUser`` is rejected by the server.
                select = [
                    "FileRef",
                    "AuthorId",
                    "EditorId",
                    "HasUniqueRoleAssignments",
                    "CheckoutUser/Id",
                    "CheckoutUser/Title",
                ]
                if moderates:
                    select.extend(_MODERATION_FIELDS)
                items = self._sp_list.items.select(select).expand(["CheckoutUser"]).get_all().execute_query()
                for item in items:
                    ref = item.properties.get("FileRef")
                    if ref:
                        authors[ref] = (
                            parse_int(item.properties.get("AuthorId")),
                            parse_int(item.properties.get("EditorId")),
                        )
                        unique[ref] = bool(item.properties.get("HasUniqueRoleAssignments"))
                        if item.properties.get("CheckoutUser"):
                            checkout.add(ref)
                        if moderates:
                            state = _moderation_state(item.properties)
                            if state:
                                moderation[ref] = state
            except Exception as e:  # noqa: BLE001 — authorship is best-effort
                self.warnings.append(f"author/editor read failed: {e}")
        self._item_authors = authors
        self._item_unique = unique
        self._item_moderation = moderation
        self._item_checkout = checkout
        return authors

    def _moderation_enabled(self) -> bool:
        """Whether the parent library enables content approval (read once)."""
        if self._moderation_on is None:
            self._moderation_on = False
            if self._sp_list is not None:
                try:
                    self._sp_list.ensure_properties(["EnableModeration"]).get().execute_query()
                    self._moderation_on = bool(self._sp_list.properties.get("EnableModeration"))
                except Exception as e:  # noqa: BLE001 — approval state is best-effort
                    self.warnings.append(f"moderation setting read failed: {e}")
        return self._moderation_on

    @property
    def supports_item_state(self) -> bool:
        """Whether approval state can be read (needs the parent library)."""
        return self._list_source is not None

    def read_item_state(self, item: MigrationItem) -> dict | None:
        """Approval state that a fresh upload would not reproduce.

        An uploaded document starts out *approved*, so only a draft/pending or
        rejected source file carries state, together with its approval comments.
        """
        if item.item_type == "folder" or self._list_source is None:
            return None
        self._file_authors()
        state = (self._item_moderation or {}).get(item.source_path)
        if not state:
            return None
        status = state.get("_ModerationStatus")
        if status is None or status == _APPROVED_STATUS:
            return None
        return state

    def close(self) -> None:
        pass


class SharePointLibraryTarget:
    """Writes files into a document library, creating folders as needed.

    Uses the simple upload for files up to ~4MB; ``write_many`` (parallel,
    ``concurrency > 1``) uses ``create_upload_session`` for larger files.

    Pass ``sp_list`` (the target library) to also replay a folder's column values: a
    folder is a list item, so a document set's metadata or a managed folder's
    department is written onto the created folder's item. ``content_type_map``
    rewrites the folder's content type id to its target counterpart, exactly as it
    does for an item record.
    """

    #: Files carry content-approval state (``apply_item_state``). Documents refuse a
    #: moderation change combined with other property writes, so it is a write of its
    #: own, applied after the timestamps that would otherwise re-approve the file.
    supports_item_state = True

    def rebind(self) -> "SharePointLibraryTarget":
        """This target on its own cloned context (see :meth:`SharePointListSource.rebind`)."""
        context = _cloned_context(self._folder)
        sp_list = _cloned_list(self._sp_list, context) if self._sp_list is not None else None
        return SharePointLibraryTarget(
            _cloned_folder(self._folder, context),
            concurrency=self._concurrency,
            sp_list=sp_list,
            content_type_map=self._content_type_map,
        )

    def __init__(
        self,
        library_folder: "Folder",
        concurrency: int = 1,
        sp_list: "SPList | None" = None,
        content_type_map: "ContentTypeMap | None" = None,
    ) -> None:
        self._folder = library_folder
        self._concurrency = concurrency
        # The folder-record mapping is the record mapping: reuse the list target so a
        # folder's Lookup/Person/taxonomy/choice values resolve the same way.
        self._sp_list = sp_list
        self._list_target = (
            SharePointListTarget(sp_list, content_type_map=content_type_map) if sp_list is not None else None
        )
        self._content_type_map = content_type_map
        self.warnings: list[str] = []
        self._login_cache: dict[int, str | None] = {}
        self._principals_cache: _TargetPrincipals | None = None
        # Author/Editor values written by ``apply_authorship`` and folded into the
        # final timestamp write so ``Editor`` isn't reset by the latter.
        self._pending_authorship: dict[str, dict] = {}
        # Target web time zone (lazily loaded) and a UTC->local conversion cache.
        self._time_zone = None
        self._local_cache: dict[str, str] = {}
        self._field_scan: SharePointListSource | None = None

    def _utc_to_local(self, *values: str | None) -> list[str | None]:
        """Convert UTC timestamp strings to web-local wall-clock (one round trip).

        Document items parse form dates in the web's locale, so the desired UTC
        instant must be converted to local wall-clock first. The conversion runs
        server-side (``TimeZone.UTCToLocalTime``) so DST is handled correctly.
        Results are cached by the exact UTC value.
        """
        if self._time_zone is None:
            self._time_zone = self._folder.context.web.regional_settings.time_zone
        outputs: list[str | None] = [None] * len(values)
        pending: dict[str, object] = {}
        assignments: list[tuple[int, str]] = []
        for index, value in enumerate(values):
            if not value:
                continue
            utc = _sp_utc_timestamp(value)
            if utc is None:
                continue
            if not utc.endswith("Z"):
                # Unparseable value: pass it through unchanged so a rejection is
                # surfaced by ``_report_rejected_fields`` rather than silently lost.
                outputs[index] = str(value)
                continue
            cached = self._local_cache.get(utc)
            if cached is not None:
                outputs[index] = cached
                continue
            instant = parse_datetime(utc)
            if instant is None:
                outputs[index] = str(value)
                continue
            if utc not in pending:
                pending[utc] = self._time_zone.utc_to_local_time(instant)
            assignments.append((index, utc))
        if pending:
            self._folder.context.execute_query()
            for utc, result in pending.items():
                local = _sp_local_timestamp(getattr(result, "value", None))
                if local is not None:
                    self._local_cache[utc] = local
            for index, utc in assignments:
                outputs[index] = self._local_cache.get(utc)
        return outputs

    def _principals(self) -> _TargetPrincipals:
        """The (lazily built) target principal/role resolver."""
        if self._principals_cache is None:
            self._principals_cache = _TargetPrincipals(self._folder.context.web, self.warnings)
        return self._principals_cache

    def label(self) -> str:
        return f"library:{self._folder.server_relative_url}"

    def _url(self, item: MigrationItem) -> str:
        return f"{(self._folder.server_relative_url or '').rstrip('/')}/{str(item.dest_path).strip('/')}"

    def exists(self, item: MigrationItem) -> bool:
        url = self._url(item)
        try:
            if item.item_type == "folder":
                self._folder.context.web.get_folder_by_server_relative_url(url).get().execute_query()
            else:
                self._folder.context.web.get_file_by_server_relative_url(url).get().execute_query()
            return True
        except Exception:  # noqa: BLE001 — a missing item surfaces as a request error
            return False

    def _ensure_folders(self, items: list[MigrationItem]) -> None:
        """Create folder items (deduplicated to deepest paths) in one round-trip."""
        paths = [str(item.dest_path).strip("/") for item in items]
        paths = [path for path in paths if path]
        if not paths:
            return
        self._folder.ensure_folders(paths)
        self._folder.context.execute_query()

    def write(self, item: MigrationItem, payload: object) -> None:
        if item.item_type == "folder":
            self._ensure_folders([item])
            if isinstance(payload, dict):
                self._apply_folder_values(item, payload)
            return
        content = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
        self._folder.upload_file(item.dest_path, content).execute_query()

    @property
    def supports_folder_records(self) -> bool:
        """Whether a folder's column values are migrated *and* comparable."""
        return self._list_target is not None

    def _apply_folder_values(self, item: MigrationItem, record: dict) -> None:
        """Write a folder's column values onto the folder's underlying list item."""
        assert self._list_target is not None
        values = _folder_record_values(record)
        if not values:
            return
        values = self._list_target.translate_record(values)
        folder_item = self._securable(item)
        for key, value in values.items():
            folder_item.set_property(key, value)
        try:
            folder_item.update().execute_query()
        except Exception as e:  # noqa: BLE001 — a folder's structure is worth more than its values
            self.warnings.append(f"folder column values for {item.dest_path!r} could not be written: {e}")

    def _folder_projection(self) -> list[str]:
        """The target's folder columns (read once) — the set the source projected."""
        if self._sp_list is None:
            return []
        if self._field_scan is None:
            # Field definitions are read by the same code on both sides: structure
            # provisioning keeps the internal names, so the projections line up.
            self._field_scan = SharePointListSource(self._sp_list)
        try:
            return self._field_scan.folder_projection()
        except Exception as e:  # noqa: BLE001 — without a projection no folder values move
            self.warnings.append(f"could not read the target columns for folder values: {e}")
            return []

    def write_many(
        self,
        items: list[MigrationItem],
        payloads: list[object],
        concurrency: int | None = None,
    ) -> list[Failure]:
        """Transfer a batch of items in parallel (fast path — the library-target transfer).

        Returns:
            List of ``(dest_path, error)`` for files that failed.
        """
        from office365.migration.sharepoint.transfer import _transfer_files_parallel

        failures: list[Failure] = []
        folders = [item for item in items if item.item_type == "folder"]
        if folders:
            try:
                self._ensure_folders(folders)
            except Exception:  # noqa: BLE001 — fall back to per-folder to attribute errors
                for folder in folders:
                    try:
                        self._ensure_folders([folder])
                    except Exception as e:  # noqa: BLE001
                        failures.append((folder.dest_path, str(e)))
        # A folder's column values can only be written once its item exists, so they
        # follow the (batched) folder creation.
        for item, payload in zip(items, payloads):
            if item.item_type == "folder" and isinstance(payload, dict):
                self._apply_folder_values(item, payload)
        files = [
            (item.dest_path, payload if isinstance(payload, bytes) else str(payload).encode("utf-8"))
            for item, payload in zip(items, payloads)
            if item.item_type != "folder"
        ]
        if files:
            failures.extend(
                _transfer_files_parallel(
                    self._folder,
                    files,
                    concurrency=concurrency or self._concurrency or 1,
                )
            )
        return failures

    def list_paths(self) -> list[str]:
        root = (self._folder.server_relative_url or "").rstrip("/")
        extra = _site_assets_scaffolding(self._folder)
        loaded_files = self._folder.get_files(recursive=True).execute_query()
        loaded_folders = self._folder.get_folders(recursive=True).execute_query()
        paths = [(f.server_relative_url or "")[len(root) :].lstrip("/") for f in loaded_files]
        paths += [f"{(f.server_relative_url or '')[len(root) :].lstrip('/')}/" for f in loaded_folders]
        # Mirror the source projection: SharePoint-owned scaffolding (``Forms/``,
        # ``desktop.ini``, and on SiteAssets the site icon + auto-provisioned
        # notebook) is recreated server-side, never migrated, so it must not be
        # reported as target-only content during verification. Source folder paths
        # carry a trailing slash; target folder paths mirror that.
        return [p for p in paths if p != "/" and not _is_system_path(p, extra)]

    def read(self, item: MigrationItem) -> bytes:
        """Download the written item's bytes (used by verification for Office files)."""
        if item.item_type == "folder":
            return b""
        file = self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
        buffer = io.BytesIO()
        file.download(buffer).execute_query()
        return buffer.getvalue()

    def checksum(self, item: MigrationItem) -> str:
        if item.item_type == "folder":
            values = self._target_folder_values(item)
            if values is None or self._list_target is None:
                return ""
            return self._list_target.content_checksum(values)
        return hashlib.md5(self.read(item)).hexdigest()

    def _target_folder_values(self, item: MigrationItem) -> dict | None:
        """The target folder's column values as they read back (``None`` if unknown)."""
        columns = self._folder_projection()
        if not columns:
            return None
        list_item = self._securable(item).select(columns).get().execute_query()
        return _folder_record_values(dict(list_item.properties))

    def modified(self, item: MigrationItem) -> str:
        """Last-modified of the target file (for incremental migration)."""
        if item.item_type == "folder":
            return ""
        file = self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
        return iso_or_none(file.time_last_modified) or ""

    def apply_timestamps(self, item: MigrationItem) -> None:
        """Best-effort: restore ``Created``/``Modified`` on the written item.

        Uses ``ValidateUpdateListItem``, the only REST path that can set these
        system fields. For files it runs as a system update
        (``bNewDocumentUpdate=True``, the CSOM ``UpdateOverwriteVersion`` path) so
        the metadata lands without creating a new version; folders have no version
        history. ``preserve_versions`` still needs the server-side API. Authorship
        values resolved for the same item ride along in this write.
        """
        form_values: dict = {}
        created, modified = self._utc_to_local(item.created, item.modified)
        if created:
            form_values["Created"] = created
        if modified:
            form_values["Modified"] = modified
        form_values.update(self._pending_authorship.pop(item.dest_path, {}))
        if not form_values:
            return
        securable = self._securable(item)
        if securable is None:
            return
        result = securable.validate_update_list_item(
            form_values,
            dates_in_utc=True,
            new_document_update=item.item_type != "folder",
        ).execute_query()
        _report_rejected_fields(result, self.warnings, f"timestamps {item.dest_path}")

    def apply_authorship(self, item: MigrationItem) -> None:
        """Best-effort: resolve ``Author``/``Editor`` and cache them for one write.

        A principal is applied only when its login name resolves to a target user
        (``EnsureUser``); unresolved principals are skipped (same-tenant only).

        Nothing is sent here: a separate write per item doubled the cost of a
        preserved run, and a system update re-approves a document, so the cached
        values are better folded into the timestamps write (or in
        :meth:`finalize_fidelity` when timestamps are not preserved).
        """
        securable = self._securable(item)
        if securable is None:
            return
        author = self._principals().user(item.author.login_name if item.author else None)
        editor = self._principals().user(item.editor.login_name if item.editor else None)
        if author is not None and _is_system_principal(author):
            author = None
        if editor is not None and _is_system_principal(editor):
            editor = None
        if author is None and editor is None:
            return
        form_values: dict[str, FieldUserValue] = {}
        if author is not None:
            form_values["Author"] = FieldUserValue(author.id, author.login_name)
        if editor is not None:
            form_values["Editor"] = FieldUserValue(editor.id, editor.login_name)
        self._pending_authorship[item.dest_path] = dict(form_values)

    def finalize_fidelity(self, item: MigrationItem) -> None:
        """Write the fidelity values that were only cached for this item.

        The last hook wins the write: with timestamps preserved that is
        :meth:`apply_timestamps`; without them it is this method, so an item costs
        one system update instead of one per property group. Runs before the
        approval write, which must stay last.
        """
        form_values = self._pending_authorship.pop(item.dest_path, {})
        if not form_values:
            return
        securable = self._securable(item)
        if securable is None:
            return
        result = securable.validate_update_list_item(
            form_values,
            dates_in_utc=True,
            new_document_update=item.item_type != "folder",
        ).execute_query()
        _report_rejected_fields(result, self.warnings, f"authorship {item.dest_path}")

    def apply_permissions(self, item: MigrationItem, permissions: list[PermissionEntry]) -> None:
        """Best-effort: replay a file's or folder's unique ACLs onto the target item.

        Same-tenant only — cross-tenant identity mapping is out of scope. See
        :func:`_replay_role_assignments` for what happens to principals, roles and
        inheritance that cannot be resolved.
        """
        securable = self._securable(item)
        if securable is None:
            return
        _replay_role_assignments(securable, self._principals(), permissions, self.warnings, item.dest_path)
        securable.context.execute_query()

    def apply_item_state(self, item: MigrationItem, state: dict) -> None:
        """Best-effort: restore a migrated file's content-approval state.

        An uploaded file starts out approved, and the timestamp/authorship system
        updates approve it again, so a source draft or rejected file would
        otherwise silently become visible. Documents reject a moderation change
        combined with other properties (``You cannot change moderation status and
        set other item properties at that same time.``), hence a separate write,
        applied last. A library without moderation enabled has no such fields: the
        write fails and is reported, never fatal.
        """
        if item.item_type == "folder" or not state:
            return
        securable = self._securable(item)
        if securable is None:
            return
        try:
            result = securable.validate_update_list_item(
                dict(state),
                dates_in_utc=True,
                new_document_update=True,
            ).execute_query()
        except Exception as e:  # noqa: BLE001 — approval state is best-effort
            self.warnings.append(f"approval state for {item.dest_path!r} could not be restored: {e}")
            return
        _report_rejected_fields(result, self.warnings, f"approval state {item.dest_path}")

    def read_metadata(self, item: MigrationItem) -> dict | None:
        """Comparable attributes of the written item (for the metadata diff)."""
        if item.item_type == "folder":
            # A folder is an item too: the timestamp system update lands on its list
            # item, and the folder resource reflects it (same read as for a file).
            folder = (
                self._folder.context.web.get_folder_by_server_relative_path(self._url(item).rstrip("/"))
                .get()
                .execute_query()
            )
            return {
                "created": iso_or_none(folder.time_created),
                "modified": iso_or_none(folder.time_last_modified),
            }
        file = self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
        metadata = {
            "created": iso_or_none(file.time_created),
            "modified": iso_or_none(file.time_last_modified),
            "size_bytes": file.length or 0,
        }
        status = self._target_moderation_status(item)
        if status is not None:
            metadata["moderation_status"] = status
        return metadata

    def _target_moderation_status(self, item: MigrationItem) -> str | None:
        """The written file's approval status, or ``None`` when not readable."""
        securable = self._securable(item)
        if securable is None:
            return None
        try:
            securable.select(["OData__ModerationStatus"]).get().execute_query()
        except Exception:  # noqa: BLE001 — a library without moderation has no such column
            return None
        status = securable.properties.get("OData__ModerationStatus")
        return None if status is None else str(status)

    def read_permissions(self, item: MigrationItem) -> list[PermissionEntry]:
        """Read the written item's *unique* role assignments (for the permission diff)."""
        securable = self._securable(item)
        if securable is None or not _has_unique_role_assignments(securable, refresh=True):
            return []
        return _read_role_assignments(securable, normalize=self._principals().normalize)

    def _fresh_securable(self, item: MigrationItem):
        """Re-read the written item so its properties reflect what was applied."""
        securable = self._securable(item)
        if securable is not None:
            securable.get().execute_query()
        return securable

    def read_authorship(self, item: MigrationItem) -> tuple[str | None, str | None]:
        """The written item's author/editor login names (for the authorship diff)."""
        securable = self._fresh_securable(item)
        if securable is None:
            return (None, None)
        properties = securable.properties
        return (
            _user_login(self._folder.context.web, properties.get("AuthorId"), self._login_cache),
            _user_login(self._folder.context.web, properties.get("EditorId"), self._login_cache),
        )

    def _securable(self, item: MigrationItem):
        url = self._url(item).rstrip("/")
        if item.item_type == "folder":
            return self._folder.context.web.get_folder_by_server_relative_path(url).list_item_all_fields
        return self._folder.context.web.get_file_by_server_relative_url(url).listItemAllFields

    def commit(self, options=None) -> None:
        self._pending_authorship.clear()
        self._local_cache.clear()

    def close(self) -> None:
        pass
