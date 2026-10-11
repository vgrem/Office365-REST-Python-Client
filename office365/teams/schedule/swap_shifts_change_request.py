from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class SwapShiftsChangeRequest(Entity):
    @property
    def recipient_shift_id(self) -> Optional[str]:
        """Gets the recipientShiftId property"""
        return self.properties.get("recipientShiftId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SwapShiftsChangeRequest"
