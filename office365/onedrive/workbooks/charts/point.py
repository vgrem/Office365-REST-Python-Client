from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.point_format import WorkbookChartPointFormat
    from office365.runtime.types.json import Json


class WorkbookChartPoint(Entity):
    """Represents a point of a series in a chart."""

    @property
    def value(self) -> Json:
        """Gets the value property"""
        from office365.runtime.types.json import Json

        return self.properties.get("value", Json())

    @property
    def format(self) -> WorkbookChartPointFormat:
        """Gets the format property"""
        from office365.onedrive.workbooks.charts.point_format import (
            WorkbookChartPointFormat,
        )

        return self.properties.get(
            "format", WorkbookChartPointFormat(self.context, ResourcePath("format", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartPoint"
