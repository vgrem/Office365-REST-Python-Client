"""Server-side migration target — build a Migration API package and ingest it.

Unlike the client-side :class:`SharePointLibraryTarget` (which uploads each file
over REST), this target accumulates files/folders into a Migration API package,
stages the blobs in Azure Storage, and submits an ingestion job — the only path
that preserves version history and authorship, plus best-effort same-tenant ACLs.

Content and manifest go to **different** containers; the caller supplies their SAS
URIs (e.g. from ``Site.provision_migration_containers``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from office365.migration.base import MigrationItem, PermissionEntry, Principal, is_puid
from office365.migration.package.builder import PackageBuilder
from office365.migration.package.staging import create_staging
from office365.migration.server_job import MigrationServerJob

if TYPE_CHECKING:
    from office365.migration.package.builder import Package

__all__ = ["SharePointPackageTarget"]

#: Base for fresh, non-system ``DeploymentRoles`` ids. The service rejects an
#: update to a *system* role (ids are ``>= 1073741824``), so synthetic ids stay
#: below that range; the service matches the role by **title** to an existing
#: permission level and creates no duplicate.
_SYNTHETIC_ROLE_BASE = 1073000000


def _resolve_site_url(site, site_url: str | None) -> str:
    """The target site URL for ``ExportSettings.xml`` (the API rejects an empty URI)."""
    resolved = site_url or getattr(site, "url", None)
    if not resolved and hasattr(site, "ensure_property"):
        site.ensure_property("Url").execute_query()
        resolved = site.url
    if not resolved:
        raise ValueError("site_url is required — ExportSettings.xml needs the target site URL")
    return resolved


class SharePointPackageTarget:
    """A ``DataTarget`` that builds a package and submits a server-side ingestion job.

    The only path that preserves version history: the runner reads each file's
    older versions (``source.read_version_history``) into the item and they ride
    the manifest's ``<Versions>`` element. Authorship and ACLs are carried too:
    ``Author``/``ModifiedBy`` become ``UserGroup.xml`` principals (matched by the
    integer id), and — with ``preserve_permissions`` — each item's role
    assignments become ``DeploymentRoles``/``DeploymentRoleAssignments`` grants for
    resolved users (best-effort, same-tenant; groups/unresolved principals are
    skipped with a warning).
    """

    # Marks this target as able to restore version history (see DataTarget).
    supports_versions = True
    # Marks this target as able to restore authorship (Author/ModifiedBy) from
    # ``item.author``/``item.editor`` (see DataTarget); best-effort (resolved users).
    supports_authorship = True

    def __init__(
        self,
        site,
        web_id,
        *,
        content_uri: str | None = None,
        manifest_uri: str | None = None,
        site_url: str | None = None,
        list_title: str = "Documents",
        list_url: str | None = None,
        web_url: str = "/",
        root_folder_id: str | None = None,
        root_folder_parent_id: str | None = None,
        source_type: str = "SharePointOnline",
        azure_queue_report_uri: str | None = None,
        encryption_key: bytes | None = None,
        staging=None,
    ) -> None:
        self._site = site
        self._web_id = web_id
        self._list_title = list_title
        self._content_uri = content_uri
        self._manifest_uri = manifest_uri
        self._azure_queue_report_uri = azure_queue_report_uri
        self._encryption_key = encryption_key
        if staging is None:
            if not (content_uri and manifest_uri):
                raise ValueError("content_uri and manifest_uri are required unless staging is provided")
            staging = create_staging(content_uri, manifest_uri, encryption_key=encryption_key)
        self._staging = staging
        self._builder = PackageBuilder(
            _resolve_site_url(site, site_url),
            web_id=web_id,
            web_url=web_url,
            list_title=list_title,
            list_url=list_url,
            root_folder_id=root_folder_id,
            root_folder_parent_id=root_folder_parent_id,
            source_type=source_type,
        )
        self.job_id: str | None = None
        self._package: "Package | None" = None
        self._web_url = web_url
        self._users: dict[str, int] = {}
        self._unresolved: set[str] = set()
        self._roles: dict[str, str] = {}
        self._role_seq = 0
        # Non-fatal fidelity gaps (skipped groups / roles), surfaced by the session.
        self.warnings: list[str] = []

    def label(self) -> str:
        return f"migration-package:{self._list_title}"

    # ── DataTarget ───────────────────────────────────────────────

    def configure(self, options) -> None:
        """Derive per-run policy from the options before writes start.

        A requested ``preserve_permissions`` switches ``ExportSettings`` to
        ``IncludeSecurity="All"`` so the service consumes the emitted ACLs.
        """
        if getattr(options, "preserve_permissions", False):
            self._builder.set_include_security("All")

    def exists(self, item: MigrationItem) -> bool:
        # The server-side API handles overwrite/merge; nothing is checked client-side.
        return False

    def write(self, item: MigrationItem, payload: object) -> None:
        author = self._ensure_user(item.author)
        editor = self._ensure_user(item.editor)
        if item.item_type == "folder":
            self._builder.add_folder(
                item.dest_path,
                time_created=item.created,
                time_last_modified=item.modified,
                author=author,
                editor=editor,
            )
            return
        content = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
        self._builder.add_file(
            item.dest_path,
            content,
            version=item.version_label or "1.0",
            versions=item.versions or None,
            time_created=item.created,
            time_last_modified=item.modified,
            author=author,
            editor=editor,
        )

    def apply_timestamps(self, item: MigrationItem) -> None:
        """No-op: the package carries ``TimeCreated``/``TimeLastModified`` per object."""

    def apply_permissions(self, item: MigrationItem, permissions: list[PermissionEntry]) -> None:
        """Emit a ``DeploymentRoleAssignments`` grant for a written file/folder.

        Only a **resolved user** (a PUID ``system_id``) can be granted server-side;
        groups and unresolved principals are skipped with a warning rather than
        failing the job. A role without a decimal mask is skipped likewise.
        """
        object_id = self._builder.object_id(item.dest_path)
        if object_id is None:
            return
        assignments: list[tuple[str, int]] = []
        for entry in permissions:
            if not is_puid(entry.system_id):
                self.warnings.append(
                    f"permission for {entry.principal_name!r} skipped: no usable PUID "
                    "(only resolved users carry ACLs on the server-side path)"
                )
                continue
            principal_id = self._register_user(entry.principal_name, entry.system_id, entry.display_name, entry.email)
            for role in entry.roles:
                role_id = self._ensure_role(role, entry.role_masks.get(role))
                if role_id is not None:
                    assignments.append((role_id, principal_id))
        if not assignments:
            return
        self._builder.add_role_assignment(
            object_id=object_id,
            object_url=self._builder.item_url(item.dest_path),
            object_type="2",
            role_def_web_id=self._web_id,
            role_def_web_url=self._web_url,
            assignments=assignments,
        )

    def _ensure_user(self, principal: "Principal | None") -> str | None:
        """Register a principal in ``UserGroup.xml`` (by login + PUID); returns its id string."""
        if principal is None or not principal.login_name:
            return None
        if not is_puid(principal.system_id):
            # Only a numeric PUID is accepted by ``UserGroup.xml``; anything else
            # (a GUID, a claims login, the app principal) fails the whole job.
            if principal.login_name not in self._unresolved:
                self._unresolved.add(principal.login_name)
                self.warnings.append(f"principal {principal.login_name!r} skipped: no usable PUID")
            return None
        return str(
            self._register_user(principal.login_name, principal.system_id, principal.display_name, principal.email)
        )

    def _register_user(
        self,
        login: str,
        system_id: str | None,
        display_name: str | None = None,
        email: str | None = None,
    ) -> int:
        if login in self._users:
            return self._users[login]
        user_id = self._builder.add_user(
            login,
            name=display_name or login,
            email=email,
            system_id=system_id,
        )
        self._users[login] = user_id
        return user_id

    def _ensure_role(self, name: str, mask: str | None) -> str | None:
        """Register a synthetic-``RoleId`` ``<Role>`` for a permission level (cached)."""
        if name in self._roles:
            return self._roles[name]
        if not mask:
            self.warnings.append(f"role {name!r} skipped: no permission mask available")
            return None
        self._role_seq += 1
        role_id = str(_SYNTHETIC_ROLE_BASE + self._role_seq)
        self._roles[name] = role_id
        self._builder.add_role(role_id, name, mask)
        return role_id

    def list_paths(self) -> list[str]:
        return []

    def checksum(self, item: MigrationItem) -> str:
        return ""

    # ── Package + submission ─────────────────────────────────────

    def build(self) -> "Package":
        """Render the package from the items written so far."""
        self._package = self._builder.build()
        return self._package

    def stage(self) -> "Package":
        """Build the package and stage its blobs for ingestion."""
        package = self.build()
        self._staging.stage(package)
        return package

    def commit(self, options=None) -> None:
        """Stage the package and submit the ingestion job (called by the runner)."""
        if not (self._content_uri and self._manifest_uri):
            raise ValueError("content_uri and manifest_uri are required to submit an ingestion job")
        self.stage()
        server = MigrationServerJob(self._site)
        if self._encryption_key is not None:
            self.job_id = server.submit_encrypted(
                self._web_id,
                self._content_uri,
                self._manifest_uri,
                self._encryption_key,
                self._azure_queue_report_uri,
            )
        else:
            self.job_id = server.submit(
                self._web_id,
                self._content_uri,
                self._manifest_uri,
                self._azure_queue_report_uri,
            )

    def monitor(self, interval: float = 5, timeout: float = 1800, progress=None) -> str:
        """Poll the submitted job to completion (``GetMigrationJobProgress``)."""
        if self.job_id is None:
            raise ValueError("no job submitted yet — call commit() first")
        return MigrationServerJob(self._site).monitor(self.job_id, interval=interval, timeout=timeout, progress=progress)

    @property
    def staging(self):
        """The staging strategy (``FileSystemStaging`` / ``BlobStaging``)."""
        return self._staging

    def events(self) -> list[dict]:
        """All progress events for the submitted job (call after :meth:`monitor`)."""
        if self.job_id is None:
            return []
        return MigrationServerJob(self._site).all_events(self.job_id)

    def errors(self) -> list[dict]:
        """The ``JobError`` events for the submitted job (call after :meth:`monitor`)."""
        if self.job_id is None:
            return []
        return MigrationServerJob(self._site).errors(self.job_id)

    def diagnose(self) -> list[str]:
        """Human-readable reasons the submitted job failed (errors, events, API log).

        The progress events omit the detail; the API writes it to a log in the
        manifest container (named by the ``JobLogFileCreate`` event), which this
        fetches — the container grants ``Read``.
        """
        if self.job_id is None:
            return []
        events = self.events()
        lines = [f"! {e.get('ErrorType', 'error')}: {e.get('Message', '')}".rstrip() for e in self.errors()]
        if not lines:
            lines = [f"· {e.get('Event')}: {e.get('Message', '')}".rstrip() for e in events]
        lines.extend(self._read_logs(events))
        return lines

    def _read_logs(self, events: list[dict]) -> list[str]:
        reader = getattr(self._staging, "read_manifest_blob", None)
        if not callable(reader):
            return []
        names = [event.get("FileName") for event in events if event.get("FileName")]
        if not names and self.job_id:
            names = [f"Import-{self.job_id}-1.log"]
        lines: list[str] = []
        for name in names:
            try:
                data = reader(name)
                text = data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)
            except Exception as exc:  # noqa: BLE001 — diagnostics are best-effort
                lines.append(f"(log {name} unavailable: {exc})")
            else:
                lines.append(f"--- {name} ---")
                lines.append(text[:4000])
        return lines

    def close(self) -> None:
        pass
