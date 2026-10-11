from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.communications.onlinemeetings.base import OnlineMeetingBase

if TYPE_CHECKING:
    from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone


class VirtualEventSession(OnlineMeetingBase):
    """Represents a session in a virtualEvent."""

    @property
    def capacity(self) -> Optional[int]:
        """Gets the capacity property"""
        return self.properties.get("capacity", None)

    @property
    def end_date_time(self) -> DateTimeTimeZone:
        """Gets the endDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("endDateTime", DateTimeTimeZone())

    @property
    def start_date_time(self) -> DateTimeTimeZone:
        """Gets the startDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("startDateTime", DateTimeTimeZone())

    @property
    def video_on_demand_web_url(self) -> Optional[str]:
        """Gets the videoOnDemandWebUrl property"""
        return self.properties.get("videoOnDemandWebUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventSession"
