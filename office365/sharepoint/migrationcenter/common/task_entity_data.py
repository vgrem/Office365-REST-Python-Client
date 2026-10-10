from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity


class MigrationTaskEntityData(Entity):
    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.MigrationCenter.Common.MigrationTaskEntityData"

    @property
    def agent_group_name(self) -> Optional[str]:
        """Gets the AgentGroupName property"""
        return self.properties.get("AgentGroupName", None)

    @property
    def azure_active_directory_lkp(self) -> Optional[bool]:
        """Gets the AzureActiveDirectoryLkp property"""
        return self.properties.get("AzureActiveDirectoryLkp", None)

    @property
    def custom_azure_access_key(self) -> Optional[str]:
        """Gets the CustomAzureAccessKey property"""
        return self.properties.get("CustomAzureAccessKey", None)

    @property
    def custom_azure_deletion_after_mig(self) -> Optional[bool]:
        """Gets the CustomAzureDeletionAfterMig property"""
        return self.properties.get("CustomAzureDeletionAfterMig", None)

    @property
    def custom_azure_storage_account(self) -> Optional[str]:
        """Gets the CustomAzureStorageAccount property"""
        return self.properties.get("CustomAzureStorageAccount", None)

    @property
    def date_created(self) -> Optional[datetime]:
        """Gets the DateCreated property"""
        return self.properties.get("DateCreated", datetime.min)

    @property
    def date_modified(self) -> Optional[datetime]:
        """Gets the DateModified property"""
        return self.properties.get("DateModified", datetime.min)

    @property
    def delta_sync_datetime_filter(self) -> Optional[datetime]:
        """Gets the DeltaSyncDateTimeFilter property"""
        return self.properties.get("DeltaSyncDateTimeFilter", datetime.min)

    @property
    def delta_sync_enabled(self) -> Optional[bool]:
        """Gets the DeltaSyncEnabled property"""
        return self.properties.get("DeltaSyncEnabled", None)

    @property
    def enable_incremental(self) -> Optional[bool]:
        """Gets the EnableIncremental property"""
        return self.properties.get("EnableIncremental", None)

    @property
    def enable_user_mappings(self) -> Optional[bool]:
        """Gets the EnableUserMappings property"""
        return self.properties.get("EnableUserMappings", None)

    @property
    def encrypted(self) -> Optional[bool]:
        """Gets the Encrypted property"""
        return self.properties.get("Encrypted", None)

    @property
    def filter_out_hidden_files(self) -> Optional[bool]:
        """Gets the FilterOutHiddenFiles property"""
        return self.properties.get("FilterOutHiddenFiles", None)

    @property
    def filter_out_path_special_characters(self) -> Optional[bool]:
        """Gets the FilterOutPathSpecialCharacters property"""
        return self.properties.get("FilterOutPathSpecialCharacters", None)

    @property
    def ignored_file_extensions(self) -> Optional[str]:
        """Gets the IgnoredFileExtensions property"""
        return self.properties.get("IgnoredFileExtensions", None)

    @property
    def invalid_chars_replacement(self) -> Optional[str]:
        """Gets the InvalidCharsReplacement property"""
        return self.properties.get("InvalidCharsReplacement", None)

    @property
    def migrate_all_web_structures(self) -> Optional[bool]:
        """Gets the MigrateAllWebStructures property"""
        return self.properties.get("MigrateAllWebStructures", None)

    @property
    def migrate_onenote_notebook(self) -> Optional[bool]:
        """Gets the MigrateOneNoteNotebook property"""
        return self.properties.get("MigrateOneNoteNotebook", None)

    @property
    def migrate_schema(self) -> Optional[bool]:
        """Gets the MigrateSchema property"""
        return self.properties.get("MigrateSchema", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)

    @property
    def preserve_permission_for_file_share(self) -> Optional[bool]:
        """Gets the PreservePermissionForFileShare property"""
        return self.properties.get("PreservePermissionForFileShare", None)

    @property
    def preserve_user_permission_for_on_prem(self) -> Optional[bool]:
        """Gets the PreserveUserPermissionForOnPrem property"""
        return self.properties.get("PreserveUserPermissionForOnPrem", None)

    @property
    def replace_invalid_chars(self) -> Optional[bool]:
        """Gets the ReplaceInvalidChars property"""
        return self.properties.get("ReplaceInvalidChars", None)

    @property
    def scan_only(self) -> Optional[bool]:
        """Gets the ScanOnly property"""
        return self.properties.get("ScanOnly", None)

    @property
    def scheduled_time_utc(self) -> Optional[datetime]:
        """Gets the ScheduledTimeUtc property"""
        return self.properties.get("ScheduledTimeUtc", datetime.min)

    @property
    def scheduled_type(self) -> Optional[int]:
        """Gets the ScheduledType property"""
        return self.properties.get("ScheduledType", None)

    @property
    def settings_up_datetime(self) -> Optional[datetime]:
        """Gets the SettingsUpdateTime property"""
        return self.properties.get("SettingsUpdateTime", datetime.min)

    @property
    def skip_list_with_audience_enabled(self) -> Optional[bool]:
        """Gets the SkipListWithAudienceEnabled property"""
        return self.properties.get("SkipListWithAudienceEnabled", None)

    @property
    def source_list_name(self) -> Optional[str]:
        """Gets the SourceListName property"""
        return self.properties.get("SourceListName", None)

    @property
    def source_list_relative_path(self) -> Optional[str]:
        """Gets the SourceListRelativePath property"""
        return self.properties.get("SourceListRelativePath", None)

    @property
    def source_uri(self) -> Optional[str]:
        """Gets the SourceUri property"""
        return self.properties.get("SourceUri", None)

    @property
    def source_user_name(self) -> Optional[str]:
        """Gets the SourceUserName property"""
        return self.properties.get("SourceUserName", None)

    @property
    def start_migration_automatically_when_no_scan_issue(self) -> Optional[bool]:
        """Gets the StartMigrationAutomaticallyWhenNoScanIssue property"""
        return self.properties.get("StartMigrationAutomaticallyWhenNoScanIssue", None)

    @property
    def tags(self) -> StringCollection:
        """Gets the Tags property"""
        return self.properties.get("Tags", StringCollection())

    @property
    def target_list_name(self) -> Optional[str]:
        """Gets the TargetListName property"""
        return self.properties.get("TargetListName", None)

    @property
    def target_list_relative_path(self) -> Optional[str]:
        """Gets the TargetListRelativePath property"""
        return self.properties.get("TargetListRelativePath", None)

    @property
    def target_site_url(self) -> Optional[str]:
        """Gets the TargetSiteUrl property"""
        return self.properties.get("TargetSiteUrl", None)

    @property
    def target_user_name(self) -> Optional[str]:
        """Gets the TargetUserName property"""
        return self.properties.get("TargetUserName", None)

    @property
    def turn_on_date_created_filter(self) -> Optional[bool]:
        """Gets the TurnOnDateCreatedFilter property"""
        return self.properties.get("TurnOnDateCreatedFilter", None)

    @property
    def turn_on_date_modified_filter(self) -> Optional[bool]:
        """Gets the TurnOnDateModifiedFilter property"""
        return self.properties.get("TurnOnDateModifiedFilter", None)

    @property
    def turn_on_extension_filter(self) -> Optional[bool]:
        """Gets the TurnOnExtensionFilter property"""
        return self.properties.get("TurnOnExtensionFilter", None)

    @property
    def type(self) -> Optional[int]:
        """Gets the Type property"""
        return self.properties.get("Type", None)

    @property
    def use_custom_azure_storage(self) -> Optional[bool]:
        """Gets the UseCustomAzureStorage property"""
        return self.properties.get("UseCustomAzureStorage", None)

    @property
    def user_mapping_csv_file(self) -> Optional[str]:
        """Gets the UserMappingCSVFile property"""
        return self.properties.get("UserMappingCSVFile", None)

    @property
    def version_nums_preserved(self) -> Optional[int]:
        """Gets the VersionNumsPreserved property"""
        return self.properties.get("VersionNumsPreserved", None)
