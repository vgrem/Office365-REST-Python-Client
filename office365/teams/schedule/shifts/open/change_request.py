from __future__ import annotations

from typing import Optional

from office365.teams.schedule.change_request import ScheduleChangeRequest


class OpenShiftChangeRequest(ScheduleChangeRequest):
    """Represents request to claim an openShift in a schedule."""

    @property
    def open_shift_id(self) -> Optional[str]:
        """Gets the openShiftId property"""
        return self.properties.get("openShiftId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OpenShiftChangeRequest"
