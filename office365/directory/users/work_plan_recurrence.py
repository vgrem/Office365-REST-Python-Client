from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.communications.presences.work_location_type import WorkLocationType
    from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
    from office365.outlook.mail.patterned_recurrence import PatternedRecurrence


class WorkPlanRecurrence(Entity):
    @property
    def end(self) -> DateTimeTimeZone:
        """Gets the end property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("end", DateTimeTimeZone())

    @property
    def place_id(self) -> Optional[str]:
        """Gets the placeId property"""
        return self.properties.get("placeId", None)

    @property
    def recurrence(self) -> PatternedRecurrence:
        """Gets the recurrence property"""
        from office365.outlook.mail.patterned_recurrence import PatternedRecurrence

        return self.properties.get("recurrence", PatternedRecurrence())

    @property
    def start(self) -> DateTimeTimeZone:
        """Gets the start property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("start", DateTimeTimeZone())

    @property
    def work_location_type(self) -> WorkLocationType:
        """Gets the workLocationType property"""
        from office365.communications.presences.work_location_type import (
            WorkLocationType,
        )

        return self.properties.get("workLocationType", WorkLocationType.unspecified)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkPlanRecurrence"
