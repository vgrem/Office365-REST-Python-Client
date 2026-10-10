from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class DeviceEntityData(Entity):
    @property
    def client_user_name(self) -> Optional[str]:
        """Gets the ClientUserName property"""
        return self.properties.get("ClientUserName", None)

    @property
    def device_name(self) -> Optional[str]:
        """Gets the DeviceName property"""
        return self.properties.get("DeviceName", None)

    @property
    def disk_space(self) -> Optional[int]:
        """Gets the DiskSpace property"""
        return self.properties.get("DiskSpace", None)

    @property
    def free_quota(self) -> Optional[int]:
        """Gets the FreeQuota property"""
        return self.properties.get("FreeQuota", None)

    @property
    def friendly_name(self) -> Optional[str]:
        """Gets the FriendlyName property"""
        return self.properties.get("FriendlyName", None)

    @property
    def group_name(self) -> Optional[str]:
        """Gets the GroupName property"""
        return self.properties.get("GroupName", None)

    @property
    def status_queue_expires_on_time_utc(self) -> datetime:
        """Gets the StatusQueueExpiresOnTimeUtc property"""
        return self.properties.get("StatusQueueExpiresOnTimeUtc", datetime.min)

    @property
    def status_queue_url(self) -> Optional[str]:
        """Gets the StatusQueueUrl property"""
        return self.properties.get("StatusQueueUrl", None)

    @property
    def target_user_name(self) -> Optional[str]:
        """Gets the TargetUserName property"""
        return self.properties.get("TargetUserName", None)

    @property
    def task_queue_expires_on_time_utc(self) -> datetime:
        """Gets the TaskQueueExpiresOnTimeUtc property"""
        return self.properties.get("TaskQueueExpiresOnTimeUtc", datetime.min)

    @property
    def task_queue_url(self) -> Optional[str]:
        """Gets the TaskQueueUrl property"""
        return self.properties.get("TaskQueueUrl", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the Version property"""
        return self.properties.get("Version", None)

    @property
    def working_folder(self) -> Optional[str]:
        """Gets the WorkingFolder property"""
        return self.properties.get("WorkingFolder", None)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MigrationCenter.Common.DeviceEntityData"

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
