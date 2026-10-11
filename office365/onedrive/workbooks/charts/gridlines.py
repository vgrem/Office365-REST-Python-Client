from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.gridlines_format import (
        WorkbookChartGridlinesFormat,
    )


class WorkbookChartGridlines(Entity):
    @property
    def visible(self) -> Optional[bool]:
        """Gets the visible property"""
        return self.properties.get("visible", None)

    @property
    def format(self) -> WorkbookChartGridlinesFormat:
        """Gets the format property"""
        from office365.onedrive.workbooks.charts.gridlines_format import (
            WorkbookChartGridlinesFormat,
        )

        return self.properties.get(
            "format", WorkbookChartGridlinesFormat(self.context, ResourcePath("format", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartGridlines"
