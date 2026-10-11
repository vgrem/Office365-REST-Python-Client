from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.admin.snapshot_job_status import SnapshotJobStatus
    from office365.directory.identity_set import IdentitySet


class ConfigurationSnapshotJob(Entity):
    @property
    def completed_date_time(self) -> Optional[datetime]:
        """Gets the completedDateTime property"""
        return self.properties.get("completedDateTime", datetime.min)

    @property
    def created_by(self) -> IdentitySet:
        """Gets the createdBy property"""
        from office365.directory.identity_set import IdentitySet

        return self.properties.get("createdBy", IdentitySet())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def error_details(self) -> StringCollection:
        """Gets the errorDetails property"""
        return self.properties.get("errorDetails", StringCollection())

    @property
    def resource_location(self) -> Optional[str]:
        """Gets the resourceLocation property"""
        return self.properties.get("resourceLocation", None)

    @property
    def resources(self) -> StringCollection:
        """Gets the resources property"""
        return self.properties.get("resources", StringCollection())

    @property
    def status(self) -> SnapshotJobStatus:
        """Gets the status property"""
        from office365.admin.snapshot_job_status import SnapshotJobStatus

        return self.properties.get("status", SnapshotJobStatus.notStarted)

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConfigurationSnapshotJob"
