from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.teams.schedule.time_off_item import TimeOffItem


class TimeOff(Entity):
    @property
    def draft_time_off(self) -> TimeOffItem:
        """Gets the draftTimeOff property"""
        from office365.teams.schedule.time_off_item import TimeOffItem

        return self.properties.get("draftTimeOff", TimeOffItem())

    @property
    def is_staged_for_deletion(self) -> Optional[bool]:
        """Gets the isStagedForDeletion property"""
        return self.properties.get("isStagedForDeletion", None)

    @property
    def shared_time_off(self) -> TimeOffItem:
        """Gets the sharedTimeOff property"""
        from office365.teams.schedule.time_off_item import TimeOffItem

        return self.properties.get("sharedTimeOff", TimeOffItem())

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TimeOff"
