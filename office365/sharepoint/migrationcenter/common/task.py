from __future__ import annotations

from datetime import datetime, time
from typing import Optional
from uuid import UUID

from office365.runtime.paths.v3.static import StaticPath
from office365.sharepoint.migrationcenter.common.task_entity_data import (
    MigrationTaskEntityData,
)


class MigrationTask(MigrationTaskEntityData):
    def __init__(self, context):
        static_path = StaticPath("Microsoft.Online.SharePoint.MigrationCenter.Service.MigrationTask")
        super().__init__(context, static_path)

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.MigrationCenter.Service.MigrationTask"

    @property
    def action_id(self) -> Optional[int]:
        """Gets the ActionId property"""
        return self.properties.get("ActionId", None)

    @property
    def client_name(self) -> Optional[str]:
        """Gets the ClientName property"""
        return self.properties.get("ClientName", None)

    @property
    def debug_command(self) -> Optional[str]:
        """Gets the DebugCommand property"""
        return self.properties.get("DebugCommand", None)

    @property
    def delta_sync_qualified(self) -> Optional[bool]:
        """Gets the DeltaSyncQualified property"""
        return self.properties.get("DeltaSyncQualified", None)

    @property
    def duration(self) -> Optional[time]:
        """Gets the Duration property"""
        return self.properties.get("Duration", None)

    @property
    def error_code(self) -> Optional[int]:
        """Gets the ErrorCode property"""
        return self.properties.get("ErrorCode", None)

    @property
    def error_message(self) -> Optional[str]:
        """Gets the ErrorMessage property"""
        return self.properties.get("ErrorMessage", None)

    @property
    def failed_times(self) -> Optional[int]:
        """Gets the FailedTimes property"""
        return self.properties.get("FailedTimes", None)

    @property
    def failed_time_utc(self) -> Optional[datetime]:
        """Gets the FailedTimeUtc property"""
        return self.properties.get("FailedTimeUtc", datetime.min)

    @property
    def failure_id(self) -> Optional[int]:
        """Gets the FailureId property"""
        return self.properties.get("FailureId", None)

    @property
    def files_scanned(self) -> Optional[int]:
        """Gets the FilesScanned property"""
        return self.properties.get("FilesScanned", None)

    @property
    def files_scanned_with_issues(self) -> Optional[int]:
        """Gets the FilesScannedWithIssues property"""
        return self.properties.get("FilesScannedWithIssues", None)

    @property
    def friendly_client_name(self) -> Optional[str]:
        """Gets the FriendlyClientName property"""
        return self.properties.get("FriendlyClientName", None)

    @property
    def is_retryable_failure(self) -> Optional[bool]:
        """Gets the IsRetryableFailure property"""
        return self.properties.get("IsRetryableFailure", None)

    @property
    def is_scan_done(self) -> Optional[bool]:
        """Gets the IsScanDone property"""
        return self.properties.get("IsScanDone", None)

    @property
    def last_finished_time_utc(self) -> Optional[datetime]:
        """Gets the LastFinishedTimeUtc property"""
        return self.properties.get("LastFinishedTimeUtc", datetime.min)

    @property
    def linked_device_id(self) -> Optional[UUID]:
        """Gets the LinkedDeviceId property"""
        return self.properties.get("LinkedDeviceId", None)

    @property
    def log_file_path(self) -> Optional[str]:
        """Gets the LogFilePath property"""
        return self.properties.get("LogFilePath", None)

    @property
    def management_status(self) -> Optional[int]:
        """Gets the ManagementStatus property"""
        return self.properties.get("ManagementStatus", None)

    @property
    def migrated_files_count(self) -> Optional[int]:
        """Gets the MigratedFilesCount property"""
        return self.properties.get("MigratedFilesCount", None)

    @property
    def next_schedule_time_utc(self) -> Optional[datetime]:
        """Gets the NextScheduleTimeUtc property"""
        return self.properties.get("NextScheduleTimeUtc", datetime.min)

    @property
    def overall_progress_percentage(self) -> Optional[int]:
        """Gets the OverallProgressPercentage property"""
        return self.properties.get("OverallProgressPercentage", None)

    @property
    def report_file_url(self) -> Optional[str]:
        """Gets the ReportFileUrl property"""
        return self.properties.get("ReportFileUrl", None)

    @property
    def run_times(self) -> Optional[int]:
        """Gets the RunTimes property"""
        return self.properties.get("RunTimes", None)

    @property
    def scan_done_time_utc(self) -> Optional[datetime]:
        """Gets the ScanDoneTimeUtc property"""
        return self.properties.get("ScanDoneTimeUtc", datetime.min)

    @property
    def scheduled_times(self) -> Optional[int]:
        """Gets the ScheduledTimes property"""
        return self.properties.get("ScheduledTimes", None)

    @property
    def start_time_utc(self) -> Optional[datetime]:
        """Gets the StartTimeUTC property"""
        return self.properties.get("StartTimeUTC", datetime.min)

    @property
    def status(self) -> Optional[int]:
        """Gets the Status property"""
        return self.properties.get("Status", None)

    @property
    def status_updated_time_utc(self) -> Optional[datetime]:
        """Gets the StatusUpdatedTimeUTC property"""
        return self.properties.get("StatusUpdatedTimeUTC", datetime.min)

    @property
    def task_created_time_utc(self) -> Optional[datetime]:
        """Gets the TaskCreatedTimeUtc property"""
        return self.properties.get("TaskCreatedTimeUtc", datetime.min)

    @property
    def task_id(self) -> Optional[UUID]:
        """Gets the TaskId property"""
        return self.properties.get("TaskId", None)

    @property
    def to_be_migrated_files_count(self) -> Optional[int]:
        """Gets the ToBeMigratedFilesCount property"""
        return self.properties.get("ToBeMigratedFilesCount", None)

    @property
    def total_bytes(self) -> Optional[int]:
        """Gets the TotalBytes property"""
        return self.properties.get("TotalBytes", None)

    @property
    def total_bytes_migrated(self) -> Optional[int]:
        """Gets the TotalBytesMigrated property"""
        return self.properties.get("TotalBytesMigrated", None)

    @property
    def update_status_only(self) -> Optional[bool]:
        """Gets the UpdateStatusOnly property"""
        return self.properties.get("UpdateStatusOnly", None)

    @property
    def update_timestamp(self) -> Optional[str]:
        """Gets the UpdateTimestamp property"""
        return self.properties.get("UpdateTimestamp", None)

    @property
    def workflow_id(self) -> Optional[UUID]:
        """Gets the WorkflowId property"""
        return self.properties.get("WorkflowId", None)

    @property
    def up_datetimestamp(self) -> Optional[str]:
        """Gets the UpdateTimestamp property"""
        return self.properties.get("UpdateTimestamp", None)
