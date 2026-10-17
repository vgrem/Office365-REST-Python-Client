"""Migration settings — the session-level surface (SPMT ``Register-SPMTMigration``).

Mirrors the parameters of ``Microsoft.SharePoint.MigrationTool.PowerShell``'s
``Register-SPMTMigration`` cmdlet (snake-cased) and maps the subset the core
enforces onto :class:`~office365.migration.base.MigrationOptions`.

The surface is wider than what the library implements, and a knob that silently
does nothing is a trap — a caller who sets ``skip_lists_with_name`` expects that
list to be skipped. So every setting the engine does *not* honor is reported by
:meth:`MigrationSettings.unhonored` (a session appends those notes to its
warnings), which keeps the honest/unhonest distinction in one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from office365.migration.base import MigrationOptions

__all__ = ["MigrationSettings"]

#: ``(field, the value the engine can honor, why anything else is not honored)``.
#: A ``None`` "honored value" means *any* truthy value is unhonorable.
_UNHONORED: tuple[tuple[str, object, str], ...] = (
    ("migration_type", "Content", "workflows are never migrated — they are reported as a handoff"),
    ("preserve_inheritance", True, "only items with a unique ACL are copied; inherited permissions stay inherited"),
    ("include_hidden_files", True, "hidden files are copied like any other file"),
    ("skip_sites_with_name", None, "subsites are filtered by include_subwebs only"),
    ("skip_lists_with_name", None, "lists are filtered by the include/exclude arguments"),
    ("skip_content_types_with_name", None, "content types are replayed wholesale per list"),
    ("replacement_of_invalid_char", None, "invalid characters are not rewritten"),
    (
        "migrate_all_site_fields_and_content_types",
        False,
        "structure is replayed per list; site columns and site content types are not registered at web scope",
    ),
    ("migrate_term_groups", False, "a session does not migrate the term store (use export_tree/import_tree)"),
    ("keep_all_versions", True, "every readable version is carried, with no cap"),
    ("number_of_versions", 10, "the package carries every readable version, so a cap is not applied"),
    ("automatic_user_mapping", True, "cross-tenant identity mapping is not implemented"),
    ("user_mapping_file", None, "cross-tenant identity mapping is not implemented"),
    ("lookup_reference_policy", 0, "lookups are remapped onto the migrated target list"),
    ("working_folder", None, "the client-side path keeps no working folder"),
    ("enable_multi_round", False, "multi-round runs are not implemented"),
    ("scan_only", False, "use the assessment scanners for a read-only inventory"),
    ("use_custom_azure_storage", False, "custom Azure storage is not wired into the package target"),
    ("custom_azure_storage_account", None, "custom Azure storage is not wired into the package target"),
    ("custom_azure_access_key", None, "custom Azure storage is not wired into the package target"),
    ("delete_temp_files_when_migration_done", False, "no temporary files are kept"),
)


@dataclass
class MigrationSettings:
    """Session-level migration settings (the ``Register-SPMTMigration`` surface)."""

    migration_type: str = "Content"  # Content | Workflow
    preserve_permissions: bool = False
    preserve_timestamps: bool = False  # client-side best-effort (SPMT preserves by default)
    preserve_authorship: bool = False  # client-side best-effort (SPMT preserves by default)
    preserve_inheritance: bool = True
    preserve_versions: bool = False
    keep_all_versions: bool = True
    number_of_versions: int = 10
    include_hidden_files: bool = True
    migrate_files_created_after: str | None = None
    migrate_files_modified_after: str | None = None
    skip_files_with_extension: list[str] = field(default_factory=list)
    skip_sites_with_name: str | None = None
    skip_lists_with_name: str | None = None
    skip_content_types_with_name: str | None = None
    replacement_of_invalid_char: str | None = None
    duplicate_page_behavior: str = "RENAME"
    automatic_user_mapping: bool = True
    user_mapping_file: str | None = None
    # use the server-side Migration API (full fidelity: versions/ACLs) instead of
    # client-side REST uploads — the SPMT path
    use_migration_api: bool = False
    use_custom_azure_storage: bool = False
    custom_azure_storage_account: str | None = None
    custom_azure_access_key: str | None = None
    enable_encryption: bool = True
    delete_temp_files_when_migration_done: bool = False
    working_folder: str | None = None
    enable_multi_round: bool = False
    scan_only: bool = False
    migrate_all_site_fields_and_content_types: bool = False
    migrate_site_settings: str = "PRESERVE_ALL_SETTINGS"
    migrate_navigation: bool = True
    #: Copy modern site pages (canvas + page metadata) instead of only reporting them.
    migrate_pages: bool = True
    migrate_term_groups: bool = True
    lookup_reference_policy: int = 0

    def unhonored(self) -> list[str]:
        """The settings that ask for behavior this library does not implement.

        One ready-to-print note per setting, so a run never reads as honoring a
        knob it ignores (a session appends them to ``session.warnings()``). A
        setting whose *default* is what the engine actually does is silent unless
        it is changed; the modes the engine does honor (``migrate_site_settings``,
        ``migrate_navigation``, ``migrate_pages``, ``duplicate_page_behavior``,
        ``preserve_*``, ``skip_files_with_extension``, ``migrate_files_*_after``,
        ``use_migration_api``) are not listed.
        """
        notes: list[str] = []
        for name, honored, reason in _UNHONORED:
            value = getattr(self, name)
            if honored is None:
                differs = bool(value)
            elif isinstance(honored, str):
                differs = str(value).strip().lower() != honored.lower()
            else:
                differs = value != honored
            if differs:
                notes.append(f"{name}={value!r} is not honored: {reason}")
        return notes

    def to_options(self, **overrides) -> MigrationOptions:
        """Build :class:`MigrationOptions` from the settings (``overrides`` win)."""
        values = {
            "preserve_permissions": self.preserve_permissions,
            "preserve_timestamps": self.preserve_timestamps,
            "preserve_authorship": self.preserve_authorship,
            "preserve_versions": self.preserve_versions,
            "exclude_patterns": [f"*.{extension.lstrip('.')}" for extension in self.skip_files_with_extension],
            "created_after": self.migrate_files_created_after,
            "modified_after": self.migrate_files_modified_after,
        }
        values.update(overrides)
        return MigrationOptions(**values)
