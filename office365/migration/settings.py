"""Migration settings — the session-level surface (SPMT ``Register-SPMTMigration``).

Mirrors the parameters of ``Microsoft.SharePoint.MigrationTool.PowerShell``'s
``Register-SPMTMigration`` cmdlet (snake-cased) and maps the subset the core
enforces onto :class:`~office365.migration.base.MigrationOptions`. Settings that
only apply to the SPMT Windows tool (``working_folder``, ``enable_multi_round``,
...) are kept for parity/documentation and ignored by the core.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from office365.migration.base import MigrationOptions

__all__ = ["MigrationSettings"]


@dataclass
class MigrationSettings:
    """Session-level migration settings (the ``Register-SPMTMigration`` surface)."""

    migration_type: str = "Content"  # Content | Workflow
    preserve_permissions: bool = False
    preserve_timestamps: bool = False  # client-side best-effort (SPMT preserves by default)
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
    migrate_term_groups: bool = True
    lookup_reference_policy: int = 0

    def to_options(self, **overrides) -> MigrationOptions:
        """Build :class:`MigrationOptions` from the settings (``overrides`` win)."""
        values = {
            "preserve_permissions": self.preserve_permissions,
            "preserve_timestamps": self.preserve_timestamps,
            "preserve_versions": self.preserve_versions,
            "exclude_patterns": [f"*.{extension.lstrip('.')}" for extension in self.skip_files_with_extension],
            "created_after": self.migrate_files_created_after,
            "modified_after": self.migrate_files_modified_after,
        }
        values.update(overrides)
        return MigrationOptions(**values)
