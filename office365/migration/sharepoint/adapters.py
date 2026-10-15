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
from collections.abc import Callable
from datetime import timezone
from typing import TYPE_CHECKING, Any, cast

from office365.migration.adapters import MigrationProgress
from office365.migration.base import MigrationItem, PermissionEntry, Principal, conflict_to_on_conflict, is_puid
from office365.migration.sharepoint.transfer import Failure
from office365.runtime.converters.json_file import record_to_json
from office365.runtime.converters.records import records_from_items
from office365.runtime.converters.scalars import iso_or_none, parse_datetime, parse_int
from office365.runtime.limits import DEFAULT_BATCH_SIZE
from office365.runtime.operations import emit_progress
from office365.sharepoint.fields.builtin_field_name import SYSTEM_FIELD_NAMES
from office365.sharepoint.principal.type import PrincipalType

if TYPE_CHECKING:
    from office365.sharepoint.files.file import File
    from office365.sharepoint.folders.folder import Folder
    from office365.sharepoint.lists.list import List as SPList
    from office365.sharepoint.permissions.roles.definitions.definition import RoleDefinition

_TAXONOMY_FIELD_TYPES = {"TaxonomyFieldType", "TaxonomyFieldTypeMulti"}

# Always-projected system metadata (reliable author/editor identity).
_METADATA_SELECT = ["AuthorId", "EditorId"]

#: Marker column added to a migrated list recording each item's source id. It makes
#: a re-run idempotent and lets post-run verification pair source and target items.
DEFAULT_LIST_IDENTITY_FIELD = "MigrationSourceId"


def _sp_timestamp(value: str | None) -> str | None:
    """Normalize an ISO-8601 timestamp to the ``...Z`` UTC form SharePoint expects.

    ``ValidateUpdateListItem`` (``datesInUTC=True``) rejects the ``+00:00`` offset
    form the migration items carry, so convert to a naive UTC ``Z`` string.
    """
    if not value:
        return None
    parsed = parse_datetime(value)
    if parsed is None:
        return value
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _is_system_path(rel: str) -> bool:
    """Whether a library-relative path is SharePoint-owned scaffolding, not user content."""
    return any(rel == entry or rel.startswith(entry + "/") for entry in _LIBRARY_SYSTEM_PATHS)


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


def _read_role_assignments(
    securable, resolve: Callable[[Any], "Principal | None"] | None = None
) -> list[PermissionEntry]:
    """Read a securable object's role assignments into ``PermissionEntry``s.

    One entry per principal (user or group), keyed by login name; the target uses
    the same shape so the permission diff compares like with like. Role names are
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
        entry = PermissionEntry(principal_name=name, roles=roles, role_masks=role_masks)
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
        # are captured reliably; an explicit/safe projection is honored as-is.
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
            result.append(
                MigrationItem(
                    source_path=f"{self._list.title}/{item_id}",
                    dest_path=item_id,
                    item_type="record",
                    modified=iso_or_none(record.get("Modified")),
                    created=iso_or_none(record.get("Created")),
                    author_id=parse_int(record.get("AuthorId")),
                    editor_id=parse_int(record.get("EditorId")),
                )
            )
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

    @staticmethod
    def _project_records(loaded) -> list[dict]:
        # Project every loaded property — not the collection's literal ``select``.
        # Passing ``["*", ...]`` straight through emitted ``{"*": None, ...}``, so
        # migrated records carried no field values at all. ``AttachmentFiles`` is a
        # navigation property (objects, not a scalar column) and is excluded; the
        # target writes attachments separately.
        select = sorted({key for item in loaded for key in item.properties if key != "AttachmentFiles"})
        return records_from_items(list(loaded), select, set(), raw=True)

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
        payload = record_to_json(self._records.get(item.dest_path, {}))
        return hashlib.md5(payload.encode("utf-8")).hexdigest()

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
    """

    # Marks this target as accepting list-item attachments as extra items (see DataTarget).
    supports_attachments = True

    def __init__(
        self,
        target_list: "SPList",
        key: str | list[str] | None = None,
        key_field: str = "MigrationKey",
        on_conflict: str | None = None,
        identity_field: str | None = DEFAULT_LIST_IDENTITY_FIELD,
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
        self._attachment_path_cache: set[str] | None = None
        self.warnings: list[str] = []

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
        """The payload plus the source-id marker (so re-runs and verify can pair items)."""
        record = cast(dict, payload)
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
        if self._identity_index is None:
            self._identity_index = self._load_identity_index()
        return self._identity_index.get(str(source_id))

    def _load_identity_index(self) -> dict:
        """Map stored source-id -> target item (built once, after records are flushed)."""
        if not self._identity_field:
            return {}
        # A read query would implicitly flush any queued writes on this context;
        # flush them explicitly first so the cached index stays consistent.
        self._flush_pending()
        items = self._list.items.select(["Id", self._identity_field]).get_all().execute_query()
        index: dict = {}
        for target_item in items:
            value = target_item.properties.get(self._identity_field)
            if value is not None:
                index[str(value)] = target_item
        return index

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
        if self._identity_index is None:
            self._identity_index = self._load_identity_index()
        return list(self._identity_index.keys()) + self._attachment_paths()

    def checksum(self, item: MigrationItem) -> str:
        if item.item_type == "attachment":
            return self._attachment_checksum(item)
        return ""

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

    def _flush(self, batch_size: int, concurrency: int) -> None:
        if not self._list.context.has_pending_request:
            return
        self._list.context.execute_batch(items_per_batch=batch_size, concurrency=concurrency)
        self._list.items.clear()
        # Records were just created/updated, so any cached source-id index is stale.
        self._identity_index = None

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
        self._item_authors: dict[str, tuple[int | None, int | None]] | None = None
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
            if not rel or rel in seen or _is_system_path(rel):
                continue
            seen.add(rel)
            result.append(MigrationItem(source_path=url, dest_path=f"{rel}/", item_type="folder"))
            emit_progress(progress, done=len(result), stage="planning", items=[folder])
        for file in loaded:
            url = file.server_relative_url or ""
            rel = _rel(url)
            if _is_system_path(rel):
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
        return _read_role_assignments(securable, resolve=self._principal_for)

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
            system_id = str(getattr(user_id_info, "NameId", None) or "") or None
            if system_id is not None and not is_puid(system_id):
                # e.g. the app principal, whose ``UserId.NameId`` is not a PUID.
                # Emitting it would fail the whole ingestion job, so drop it.
                self.warnings.append(
                    f"user {key} ({user.login_name!r}) has no usable PUID; authorship and ACL are skipped for it"
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
        if self._sp_list is not None:
            try:
                items = self._sp_list.items.select(["FileRef", "AuthorId", "EditorId"]).get_all().execute_query()
                for item in items:
                    ref = item.properties.get("FileRef")
                    if ref:
                        authors[ref] = (
                            parse_int(item.properties.get("AuthorId")),
                            parse_int(item.properties.get("EditorId")),
                        )
            except Exception as e:  # noqa: BLE001 — authorship is best-effort
                self.warnings.append(f"author/editor read failed: {e}")
        self._item_authors = authors
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
        self._role_definitions: dict[str, RoleDefinition] | None = None

    def label(self) -> str:
        return f"library:{self._folder.server_relative_url}"

    def _url(self, item: MigrationItem) -> str:
        return f"{(self._folder.server_relative_url or '').rstrip('/')}/{item.dest_path}"

    def exists(self, item: MigrationItem) -> bool:
        try:
            self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
            return True
        except Exception:  # noqa: BLE001 — a missing file surfaces as a request error
            return False

    def write(self, item: MigrationItem, payload: object) -> None:
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

        files = [
            (item.dest_path, payload if isinstance(payload, bytes) else str(payload).encode("utf-8"))
            for item, payload in zip(items, payloads)
        ]
        return _transfer_files_parallel(
            self._folder,
            files,
            concurrency=concurrency or self._concurrency or 1,
        )

    def list_paths(self) -> list[str]:
        root = (self._folder.server_relative_url or "").rstrip("/")
        loaded = self._folder.get_files(recursive=True).execute_query()
        return [(f.server_relative_url or "")[len(root) :].lstrip("/") for f in loaded]

    def checksum(self, item: MigrationItem) -> str:
        file = self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
        buffer = io.BytesIO()
        file.download(buffer).execute_query()
        return hashlib.md5(buffer.getvalue()).hexdigest()

    def modified(self, item: MigrationItem) -> str:
        """Last-modified of the target file (for incremental migration)."""
        file = self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
        return iso_or_none(file.time_last_modified) or ""

    def apply_timestamps(self, item: MigrationItem) -> None:
        """Best-effort: restore ``Created``/``Modified`` on the written item.

        Uses ``ValidateUpdateListItem`` (the same mechanism as
        ``ListItem.system_update``), which is the only REST path that can set these
        system fields. ``preserve_versions`` still needs the server-side API.
        """
        form_values: dict[str, str] = {}
        created = _sp_timestamp(item.created)
        modified = _sp_timestamp(item.modified)
        if created:
            form_values["Created"] = created
        if modified:
            form_values["Modified"] = modified
        if not form_values:
            return
        securable = self._securable(item)
        if securable is None:
            return
        securable.validate_update_list_item(
            form_values,
            dates_in_utc=True,
            new_document_update=item.item_type != "folder",
        ).execute_query()

    def apply_permissions(self, item: MigrationItem, permissions: list[PermissionEntry]) -> None:
        """Best-effort: break inheritance and recreate the source role assignments.

        Principals are resolved by login name on the target; roles that don't exist
        there are skipped. This is a same-tenant copy — cross-tenant identity
        mapping is out of scope.
        """
        securable = self._securable(item)
        if securable is None:
            return
        securable.break_role_inheritance(copy_role_assignments=False, clear_sub_scopes=False)
        for entry in permissions:
            for role_name in entry.roles:
                role = self._role_definition(role_name)
                if role is not None:
                    securable.add_role_assignment(entry.principal_name, role)
        securable.context.execute_query()

    def read_metadata(self, item: MigrationItem) -> dict | None:
        """Comparable attributes of the written item (for the metadata diff)."""
        file = self._folder.context.web.get_file_by_server_relative_url(self._url(item)).get().execute_query()
        return {
            "created": iso_or_none(file.time_created),
            "modified": iso_or_none(file.time_last_modified),
            "size_bytes": file.length or 0,
        }

    def read_permissions(self, item: MigrationItem) -> list[PermissionEntry]:
        """Read the written item's role assignments (for the permission diff)."""
        securable = self._securable(item)
        if securable is None:
            return []
        return _read_role_assignments(securable)

    def _securable(self, item: MigrationItem):
        url = self._url(item).rstrip("/")
        if item.item_type == "folder":
            return self._folder.context.web.get_folder_by_server_relative_path(url).list_item_all_fields
        return self._folder.context.web.get_file_by_server_relative_url(url).listItemAllFields

    def _role_definition(self, name: str) -> "RoleDefinition | None":
        """Resolve (and cache) a target role definition by name."""
        if self._role_definitions is None:
            loaded = self._folder.context.web.role_definitions.get().execute_query()
            self._role_definitions = {rd.name: rd for rd in loaded if rd.name}
        return self._role_definitions.get(name)

    def commit(self, options=None) -> None:
        pass

    def close(self) -> None:
        pass
