from __future__ import annotations

from office365.entity import Entity


class WorkbookChartFill(Entity):
    """Represents the fill formatting for a chart element."""

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartFill"
