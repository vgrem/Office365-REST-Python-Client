from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity
from office365.security.search.datasourcecontainerstatus import DataSourceContainerStatus
from office365.security.search.datasourceholdstatus import DataSourceHoldStatus


class DataSourceContainer(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def hold_status(self) -> DataSourceHoldStatus:
        """Gets the holdStatus property"""
        return self.properties.get("holdStatus", DataSourceHoldStatus.notApplied)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def released_date_time(self) -> Optional[datetime]:
        """Gets the releasedDateTime property"""
        return self.properties.get("releasedDateTime", datetime.min)

    @property
    def status(self) -> DataSourceContainerStatus:
        """Gets the status property"""
        return self.properties.get("status", DataSourceContainerStatus.active)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DataSourceContainer"
