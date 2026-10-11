from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.outlook.calendar.schedule.open_shift_item import OpenShiftItem


class OpenShift(Entity):
    @property
    def draft_open_shift(self) -> OpenShiftItem:
        """Gets the draftOpenShift property"""
        from office365.outlook.calendar.schedule.open_shift_item import OpenShiftItem

        return self.properties.get("draftOpenShift", OpenShiftItem())

    @property
    def is_staged_for_deletion(self) -> Optional[bool]:
        """Gets the isStagedForDeletion property"""
        return self.properties.get("isStagedForDeletion", None)

    @property
    def scheduling_group_id(self) -> Optional[str]:
        """Gets the schedulingGroupId property"""
        return self.properties.get("schedulingGroupId", None)

    @property
    def shared_open_shift(self) -> OpenShiftItem:
        """Gets the sharedOpenShift property"""
        from office365.outlook.calendar.schedule.open_shift_item import OpenShiftItem

        return self.properties.get("sharedOpenShift", OpenShiftItem())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OpenShift"
