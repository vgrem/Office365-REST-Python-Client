from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class Device(Entity):
    @property
    def action_id(self) -> Optional[int]:
        """Gets the ActionId property"""
        return self.properties.get("ActionId", None)

    @property
    def assigned_time_utc(self) -> datetime:
        """Gets the AssignedTimeUTC property"""
        return self.properties.get("AssignedTimeUTC", datetime.min)

    @property
    def assignment_id(self) -> Optional[str]:
        """Gets the AssignmentId property"""
        return self.properties.get("AssignmentId", None)

    @property
    def debug_command(self) -> Optional[str]:
        """Gets the DebugCommand property"""
        return self.properties.get("DebugCommand", None)

    @property
    def device_added_time_utc(self) -> datetime:
        """Gets the DeviceAddedTimeUTC property"""
        return self.properties.get("DeviceAddedTimeUTC", datetime.min)

    @property
    def disconnected(self) -> Optional[bool]:
        """Gets the Disconnected property"""
        return self.properties.get("Disconnected", None)

    @property
    def error_code(self) -> Optional[str]:
        """Gets the ErrorCode property"""
        return self.properties.get("ErrorCode", None)

    @property
    def error_message(self) -> Optional[str]:
        """Gets the ErrorMessage property"""
        return self.properties.get("ErrorMessage", None)

    @property
    def from_client(self) -> Optional[bool]:
        """Gets the FromClient property"""
        return self.properties.get("FromClient", None)

    @property
    def last_activity_time_utc(self) -> datetime:
        """Gets the LastActivityTimeUtc property"""
        return self.properties.get("LastActivityTimeUtc", datetime.min)

    @property
    def last_heartbeat_time_utc(self) -> datetime:
        """Gets the LastHeartbeatTimeUtc property"""
        return self.properties.get("LastHeartbeatTimeUtc", datetime.min)

    @property
    def last_modified_time_utc(self) -> datetime:
        """Gets the LastModifiedTimeUtc property"""
        return self.properties.get("LastModifiedTimeUtc", datetime.min)

    @property
    def linked_task_id(self) -> Optional[UUID]:
        """Gets the LinkedTaskId property"""
        return self.properties.get("LinkedTaskId", None)

    @property
    def message(self) -> Optional[str]:
        """Gets the Message property"""
        return self.properties.get("Message", None)

    @property
    def running_task_count(self) -> Optional[int]:
        """Gets the RunningTaskCount property"""
        return self.properties.get("RunningTaskCount", None)

    @property
    def status(self) -> Optional[int]:
        """Gets the Status property"""
        return self.properties.get("Status", None)

    @property
    def update_timestamp(self) -> Optional[str]:
        """Gets the UpdateTimestamp property"""
        return self.properties.get("UpdateTimestamp", None)

    @property
    def waiting_task_count(self) -> Optional[int]:
        """Gets the WaitingTaskCount property"""
        return self.properties.get("WaitingTaskCount", None)

    @property
    def workflow_json_data(self) -> Optional[str]:
        """Gets the WorkflowJsonData property"""
        return self.properties.get("WorkflowJsonData", None)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MigrationCenter.Service.Device"

    @property
    def up_datetimestamp(self) -> Optional[str]:
        """Gets the UpdateTimestamp property"""
        return self.properties.get("UpdateTimestamp", None)
