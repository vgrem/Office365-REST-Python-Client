from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.axis_title_format import (
        WorkbookChartAxisTitleFormat,
    )


class WorkbookChartAxisTitle(Entity):
    @property
    def text(self) -> Optional[str]:
        """Gets the text property"""
        return self.properties.get("text", None)

    @property
    def visible(self) -> Optional[bool]:
        """Gets the visible property"""
        return self.properties.get("visible", None)

    @property
    def format(self) -> WorkbookChartAxisTitleFormat:
        """Gets the format property"""
        from office365.onedrive.workbooks.charts.axis_title_format import (
            WorkbookChartAxisTitleFormat,
        )

        return self.properties.get(
            "format", WorkbookChartAxisTitleFormat(self.context, ResourcePath("format", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartAxisTitle"
