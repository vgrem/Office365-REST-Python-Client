from __future__ import annotations

from office365.entity import Entity


class WorkbookRangeSort(Entity):
    """Manages sorting operations on Range objects."""

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookRangeSort"
