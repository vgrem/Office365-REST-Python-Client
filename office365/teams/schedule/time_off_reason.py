from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.teams.schedule.change_tracked_entity import ChangeTrackedEntity

if TYPE_CHECKING:
    from office365.teams.schedule.time_off_reason_icon_type import TimeOffReasonIconType


class TimeOffReason(ChangeTrackedEntity):
    """Represents a valid reason to take time off in a schedule."""

    @property
    def code(self) -> Optional[str]:
        """Gets the code property"""
        return self.properties.get("code", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def icon_type(self) -> TimeOffReasonIconType:
        """Gets the iconType property"""
        from office365.teams.schedule.time_off_reason_icon_type import (
            TimeOffReasonIconType,
        )

        return self.properties.get("iconType", TimeOffReasonIconType.none)

    @property
    def is_active(self) -> Optional[bool]:
        """Gets the isActive property"""
        return self.properties.get("isActive", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TimeOffReason"
