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
from typing import TYPE_CHECKING, cast

from office365.migration.adapters import MigrationProgress
from office365.migration.base import MigrationItem, PermissionEntry, conflict_to_on_conflict
from office365.migration.sharepoint.transfer import Failure
from office365.runtime.converters.json_file import record_to_json
from office365.runtime.converters.scalars import iso_or_none, parse_datetime, parse_int
from office365.runtime.limits import DEFAULT_BATCH_SIZE
from office365.runtime.operations import emit_progress
from office365.sharepoint.fields.builtin_field_name import SYSTEM_FIELD_NAMES

if TYPE_CHECKING:
    from office365.sharepoint.files.file import File
    from office365.sharepoint.folders.folder import Folder
    from office365.sharepoint.lists.list import List as SPList
    from office365.sharepoint.permissions.roles.definitions.definition import RoleDefinition

_TAXONOMY_FIELD_TYPES = {"TaxonomyFieldType", "TaxonomyFieldTypeMulti"}

# Always-projected system metadata (reliable author/editor identity).
_METADATA_SELECT = ["AuthorId", "EditorId"]


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


class SharePointListSource:
    """Enumerates a SharePoint list's items into record migration items."""

    def __init__(self, source_list: "SPList", select: list[str] | None = None) -> None:
        self._list = source_list
        self._select = select
        self._records: dict[str, dict] = {}
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
        return items.select(columns).get_all().execute_query()

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
        from office365.runtime.converters.records import iter_records

        # Reuse the shared record projection (raw values, no JSON coercion) so the
        # migration payload matches the data pipeline's.
        records = iter_records(loaded, raw=True)
        result: list[MigrationItem] = []
        for item, record in zip(loaded, records):
            self._records[str(item.id)] = record
            result.append(
                MigrationItem(
                    source_path=f"{self._list.title}/{item.id}",
                    dest_path=str(item.id),
                    item_type="record",
                    modified=iso_or_none(record.get("Modified")),
                    created=iso_or_none(record.get("Created")),
                    author_id=parse_int(record.get("AuthorId")),
                    editor_id=parse_int(record.get("EditorId")),
                )
            )
            emit_progress(progress, done=len(result), stage="planning", items=[item])
        return result

    def read(self, item: MigrationItem) -> dict:
        return self._records.get(item.dest_path, {})

    def checksum(self, item: MigrationItem) -> str:
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
    """

    def __init__(
        self,
        target_list: "SPList",
        key: str | list[str] | None = None,
        key_field: str = "MigrationKey",
        on_conflict: str | None = None,
    ) -> None:
        self._list = target_list
        self._key_columns = [key] if isinstance(key, str) else (list(key) if key else [])
        self._key_field = key_field
        self._on_conflict_override = on_conflict
        self._on_conflict = on_conflict or "skip"
        self._target = None
        self._existing: dict = {}

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
        # Keyed dedup happens in _queue (the key is derived from the payload, which
        # exists() doesn't receive); without a key, records are appended.
        return False

    def write(self, item: MigrationItem, payload: object) -> None:
        self._queue([cast(dict, payload)])

    def write_many(
        self,
        items: list[MigrationItem],
        payloads: list[object],
        concurrency: int = 1,
    ) -> list[Failure]:
        """Queue a chunk and flush it immediately, then discard the entities.

        Flushing per chunk (instead of only at :meth:`commit`) keeps a large list
        migration memory-bounded — the queued creates never accumulate for the
        whole run.

        Returns:
            No failures (a batch failure raises; there are no partial successes).
        """
        self._queue([cast(dict, payload) for payload in payloads])
        self._flush(len(payloads), concurrency)
        return []

    def _queue(self, records: list[dict]) -> None:
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

    def list_paths(self) -> list[str]:
        return [str(i.id) for i in self._list.items.get().execute_query()]

    def checksum(self, item: MigrationItem) -> str:
        return ""

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
    ) -> None:
        self._folder = library_folder
        self._files: dict[str, "File"] = {}
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

        def _rel(url: str) -> str:
            return url[len(root) :].lstrip("/") if root else url.lstrip("/")

        result: list[MigrationItem] = []
        seen: set[str] = set()
        for folder in loaded_folders:
            url = folder.server_relative_url or ""
            rel = _rel(url)
            if not rel or rel in seen:
                continue
            seen.add(rel)
            result.append(MigrationItem(source_path=url, dest_path=f"{rel}/", item_type="folder"))
            emit_progress(progress, done=len(result), stage="planning", items=[folder])
        for file in loaded:
            url = file.server_relative_url or ""
            rel = _rel(url)
            self._files[rel] = file
            result.append(
                MigrationItem(
                    source_path=url,
                    dest_path=rel,
                    size_bytes=file.length or 0,
                    item_type="file",
                    modified=iso_or_none(file.time_last_modified),
                    created=iso_or_none(file.time_created),
                    author_id=parse_int(file.author.id),
                    editor_id=parse_int(file.modified_by.id),
                )
            )
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
        assignments = securable.role_assignments.expand(["Member", "RoleDefinitionBindings"]).get().execute_query()
        result: list[PermissionEntry] = []
        for assignment in assignments:
            member = assignment.member
            name = member.login_name or member.user_principal_name
            if not name:
                continue
            roles = [r.name for r in assignment.role_definition_bindings if r.name]
            result.append(PermissionEntry(principal_name=name, roles=roles))
        return result

    def _securable(self, item: MigrationItem):
        if item.item_type == "folder":
            return self._folder.context.web.get_folder_by_server_relative_path(item.source_path).list_item_all_fields
        file = self._files.get(item.dest_path)
        return file.listItemAllFields if file is not None else None

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
