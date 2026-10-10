from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class SPTenantIBInsightsReportMetadata(Entity):
    """ """

    @property
    def complete_time_in_utc(self) -> datetime:
        """Gets the CompleteTimeInUtc property"""
        return self.properties.get("CompleteTimeInUtc", datetime.min)

    @property
    def queued_time_in_utc(self) -> datetime:
        """Gets the QueuedTimeInUtc property"""
        return self.properties.get("QueuedTimeInUtc", datetime.min)

    @property
    def start_time_in_utc(self) -> datetime:
        """Gets the StartTimeInUtc property"""
        return self.properties.get("StartTimeInUtc", datetime.min)

    @property
    def state(self) -> Optional[str]:
        """Gets the State property"""
        return self.properties.get("State", None)

    @property
    def entity_type_name(self):  # type: ignore[override]
        return "Microsoft.SharePoint.Insights.SPTenantIBInsightsReportMetadata"

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
