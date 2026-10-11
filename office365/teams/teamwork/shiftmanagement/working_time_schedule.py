from __future__ import annotations

from office365.entity import Entity


class WorkingTimeSchedule(Entity):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkingTimeSchedule"
