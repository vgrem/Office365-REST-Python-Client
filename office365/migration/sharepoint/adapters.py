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

from office365.migration.adapters import MigrationProgress
from office365.migration.base import MigrationItem, PermissionEntry, Principal, conflict_to_on_conflict, is_puid
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
    }
)


def _content_checksum(record: dict, extra_excluded: "frozenset[str]" = frozenset()) -> str:
    """MD5 of an item's scalar content columns in a stable, order-independent form.

    The list source and target both use this so record content can be reconciled:
    only scalar, non-excluded columns are hashed and keys are sorted, so the two
    sides agree regardless of property iteration order.
    """
    content = {
        key: value
        for key, value in record.items()
        if key not in _CONTENT_EXCLUDED
        and key not in extra_excluded
        and (value is None or isinstance(value, (str, int, float, bool)))
    }
    payload = json.dumps(content, sort_keys=True, default=str)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


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


def _has_unique_role_assignments(securable) -> bool:
    """Whether a securable has unique (broken-inheritance) role assignments.

    SharePoint REST returns *inherited* role assignments too, so reading them
    verbatim would break inheritance on every item and replicate the parent ACL.
    Only items with unique assignments are read/applied (and compared by the
    verifier); inherited items stay inherited on the target.
    """
    unique = getattr(securable, "has_unique_role_assignments", None)
    if unique is None:
        try:
            securable.ensure_property("HasUniqueRoleAssignments").execute_query()
        except Exception:  # noqa: BLE001 — an unreadable flag is treated as "not unique"
            return False
        unique = getattr(securable, "has_unique_role_assignments", None)
    return bool(unique)


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

    def __init__(self, source_list: "SPList", select: list[str] | None = None) -> None:
        self._list = source_list
        self._select = select
        self._records: dict[str, dict] = {}
        self._items: dict[str, Any] = {}
        self._attachments: dict[str, Any] = {}
        self._users: dict[int, Principal | None] = {}
        self._default_groups: _DefaultGroups | None = None
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

    def _load_items(self, select: list[str] | None):
        items = self._list.items
        # A full read projects ``*`` plus the system metadata so author/editor ids
        # and the unique-ACL flag are captured in one query (``*`` omits them);
        # an explicit/safe projection is honored as-is.
        columns = ["*", *_METADATA_SELECT] if select is None else select
        query = items.select(columns)
        if select is None:
            # Expand attachments so they can be migrated alongside their item.
            query = query.expand(["AttachmentFiles"])
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

    def _project_records(self, loaded) -> list[dict]:
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
        for record in records:
            for key, value in list(record.items()):
                if value is not None and not isinstance(value, (str, int, float, bool)):
                    record.pop(key)
                    if key not in _NAVIGATION_SELECT:
                        dropped.add(key)
        if dropped:
            self.warnings.append(
                f"skipped non-scalar column(s) with no typed-value mapping: {', '.join(sorted(dropped))}"
            )
        return records

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
        return _content_checksum(self._records.get(item.dest_path, {}))

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
            system_id = str(getattr(user_id_info, "NameId", None) or "") or None
            if system_id is not None and not is_puid(system_id):
                system_id = None
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

    #: The single-item :meth:`write` only queues a create; a chunk must be flushed
    #: before it is durable. The runner therefore routes this target through the
    #: chunked path even at ``concurrency == 1``, so checkpoints never record
    #: ``DONE`` ahead of the actual write.
    deferred_writes = True

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
        self.warnings: list[str] = []
        self._principals_cache: _TargetPrincipals | None = None

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
        return record

    def _queue(self, records: list[dict]) -> None:
        self._ensure_identity()
        if not self._key_columns:
            for record in records:
                self._list.items.queue_records([record])
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
            target,
            records,
            key_columns=key_columns,
            existing=self._existing,
            on_conflict=self._on_conflict,
        )

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
        extra = frozenset({self._identity_field}) if self._identity_field else frozenset()
        return _content_checksum(target_item.properties, extra)

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

        Uses ``ValidateUpdateListItem`` (the only REST path that can set these
        system fields); ``datesInUTC=True`` requires the ``...Z`` UTC form. When
        authorship was applied for the same item, its ``Author``/``Editor`` values
        are folded into this final write -- otherwise the update would silently
        reset ``Editor`` to the caller's identity.
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
        if form_values:
            result = target_item.validate_update_list_item(form_values, dates_in_utc=True).execute_query()
            _report_rejected_fields(result, self.warnings, f"timestamps {item.dest_path}")

    def apply_authorship(self, item: MigrationItem) -> None:
        """Best-effort: restore ``Author``/``Editor`` from the source principals.

        A principal is applied only when its login name resolves to a target user
        (``EnsureUser``); unresolved principals are skipped (same-tenant only).
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
        if author is None and editor is None:
            return
        form_values: dict[str, FieldUserValue] = {}
        if author is not None:
            form_values["Author"] = FieldUserValue(author.id, author.login_name)
        if editor is not None:
            form_values["Editor"] = FieldUserValue(editor.id, editor.login_name)
        self._pending_authorship[item.dest_path] = dict(form_values)
        result = target_item.validate_update_list_item(form_values, dates_in_utc=True).execute_query()
        _report_rejected_fields(result, self.warnings, f"authorship {item.dest_path}")

    def apply_permissions(self, item: MigrationItem, permissions: list[PermissionEntry]) -> None:
        """Best-effort: break inheritance and recreate the source's unique ACLs.

        Principals are resolved on the target by login name (users via
        ``EnsureUser``, groups by name); unresolved principals and roles are
        skipped. Same-tenant only — cross-tenant identity mapping is out of scope.
        """
        target_item = self._target_item(item)
        if target_item is None:
            return
        target_item.break_role_inheritance(copy_role_assignments=False, clear_sub_scopes=False)
        for entry in permissions:
            principal = self._principals().principal(entry.principal_name)
            if principal is None:
                continue
            for role_name in entry.roles:
                role = self._principals().role(role_name)
                if role is not None:
                    target_item.add_role_assignment(principal, role)
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
        if target_item is None or not _has_unique_role_assignments(target_item):
            return []
        return _read_role_assignments(target_item, normalize=self._principals().normalize)

    def close(self) -> None:
        pass


class SharePointLibrarySource:
    """Enumerates a document library's files and folders (recursively) for migration.

    Folder entries (``item_type="folder"``, trailing ``/`` on the destination)
    preserve the folder structure — including **empty** folders — on the target.
    """

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
        self._files: dict[str, "File"] = {}
        self._users: dict[int, "Principal | None"] = {}
        self._default_groups: _DefaultGroups | None = None
        self._item_authors: dict[str, tuple[int | None, int | None]] | None = None
        self._item_unique: dict[str, bool] | None = None
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
            result.append(MigrationItem(source_path=url, dest_path=f"{rel}/", item_type="folder"))
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
        return result

    def read(self, item: MigrationItem) -> bytes:
        if item.item_type == "folder":
            return b""
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

    def checksum(self, item: MigrationItem) -> str:
        if item.item_type == "folder":
            return hashlib.md5(b"").hexdigest()
        return hashlib.md5(self.read(item)).hexdigest()

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
        file = self._files.get(item.dest_path)
        if file is None:
            return None
        return {
            "created": iso_or_none(file.time_created),
            "modified": iso_or_none(file.time_last_modified),
            "size_bytes": file.length or 0,
        }

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
            system_id = str(raw_id or "") or None
            if system_id is not None and not is_puid(system_id):
                # e.g. the app principal, whose ``UserId.NameId`` is not a PUID.
                # Emitting it would fail the whole ingestion job, so drop it.
                self.warnings.append(
                    f"user {key} ({user.login_name!r}) has no usable PUID ({system_id!r}); "
                    "it is omitted from the server-side user map"
                )
                system_id = None
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
        if self._sp_list is not None:
            try:
                items = (
                    self._sp_list.items.select(["FileRef", "AuthorId", "EditorId", "HasUniqueRoleAssignments"])
                    .get_all()
                    .execute_query()
                )
                for item in items:
                    ref = item.properties.get("FileRef")
                    if ref:
                        authors[ref] = (
                            parse_int(item.properties.get("AuthorId")),
                            parse_int(item.properties.get("EditorId")),
                        )
                        unique[ref] = bool(item.properties.get("HasUniqueRoleAssignments"))
            except Exception as e:  # noqa: BLE001 — authorship is best-effort
                self.warnings.append(f"author/editor read failed: {e}")
        self._item_authors = authors
        self._item_unique = unique
        return authors

    def close(self) -> None:
        pass


class SharePointLibraryTarget:
    """Writes files into a document library, creating folders as needed.

    Uses the simple upload for files up to ~4MB; ``write_many`` (parallel,
    ``concurrency > 1``) uses ``create_upload_session`` for larger files.
    """

    def __init__(self, library_folder: "Folder", concurrency: int = 1) -> None:
        self._folder = library_folder
        self._concurrency = concurrency
        self.warnings: list[str] = []
        self._login_cache: dict[int, str | None] = {}
        self._principals_cache: _TargetPrincipals | None = None
        # Author/Editor values written by ``apply_authorship`` and folded into the
        # final timestamp write so ``Editor`` isn't reset by the latter.
        self._pending_authorship: dict[str, dict] = {}
        # Target web time zone (lazily loaded) and a UTC->local conversion cache.
        self._time_zone = None
        self._local_cache: dict[str, str] = {}

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
            return
        content = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
        self._folder.upload_file(item.dest_path, content).execute_query()

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
            return hashlib.md5(b"").hexdigest()
        return hashlib.md5(self.read(item)).hexdigest()

    def modified(self, item: MigrationItem) -> str:
        """Last-modified of the target file (for incremental migration)."""
        if item.item_type == "folder":
            return ""
        file = self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
        return iso_or_none(file.time_last_modified) or ""

    def apply_timestamps(self, item: MigrationItem) -> None:
        """Best-effort: restore ``Created``/``Modified`` on the written item.

        Uses ``ValidateUpdateListItem`` (the same mechanism as
        ``ListItem.system_update``), which is the only REST path that can set these
        system fields. ``preserve_versions`` still needs the server-side API.
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
        """Best-effort: restore ``Author``/``Editor`` from the source principals.

        A principal is applied only when its login name resolves to a target user
        (``EnsureUser``); unresolved principals are skipped (same-tenant only).
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
        result = securable.validate_update_list_item(
            form_values,
            dates_in_utc=True,
            new_document_update=item.item_type != "folder",
        ).execute_query()
        _report_rejected_fields(result, self.warnings, f"authorship {item.dest_path}")

    def apply_permissions(self, item: MigrationItem, permissions: list[PermissionEntry]) -> None:
        """Best-effort: break inheritance and recreate the source role assignments.

        Principals are resolved on the target by login name (users via
        ``EnsureUser``, groups by name); unresolved principals and roles are
        skipped. Same-tenant only — cross-tenant identity mapping is out of scope.
        """
        securable = self._securable(item)
        if securable is None:
            return
        securable.break_role_inheritance(copy_role_assignments=False, clear_sub_scopes=False)
        for entry in permissions:
            principal = self._principals().principal(entry.principal_name)
            if principal is None:
                continue
            for role_name in entry.roles:
                role = self._principals().role(role_name)
                if role is not None:
                    securable.add_role_assignment(principal, role)
        securable.context.execute_query()

    def read_metadata(self, item: MigrationItem) -> dict | None:
        """Comparable attributes of the written item (for the metadata diff)."""
        if item.item_type == "folder":
            return None
        file = self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
        return {
            "created": iso_or_none(file.time_created),
            "modified": iso_or_none(file.time_last_modified),
            "size_bytes": file.length or 0,
        }

    def read_permissions(self, item: MigrationItem) -> list[PermissionEntry]:
        """Read the written item's *unique* role assignments (for the permission diff)."""
        securable = self._securable(item)
        if securable is None or not _has_unique_role_assignments(securable):
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
