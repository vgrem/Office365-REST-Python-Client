from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class DeviceConfigurationUserOverview(Entity):
    @property
    def configuration_version(self) -> Optional[int]:
        """Gets the configurationVersion property"""
        return self.properties.get("configurationVersion", None)

    @property
    def error_count(self) -> Optional[int]:
        """Gets the errorCount property"""
        return self.properties.get("errorCount", None)

    @property
    def failed_count(self) -> Optional[int]:
        """Gets the failedCount property"""
        return self.properties.get("failedCount", None)

    @property
    def last_update_date_time(self) -> Optional[datetime]:
        """Gets the lastUpdateDateTime property"""
        return self.properties.get("lastUpdateDateTime", datetime.min)

    @property
    def not_applicable_count(self) -> Optional[int]:
        """Gets the notApplicableCount property"""
        return self.properties.get("notApplicableCount", None)

    @property
    def pending_count(self) -> Optional[int]:
        """Gets the pendingCount property"""
        return self.properties.get("pendingCount", None)

    @property
    def success_count(self) -> Optional[int]:
        """Gets the successCount property"""
        return self.properties.get("successCount", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceConfigurationUserOverview"
