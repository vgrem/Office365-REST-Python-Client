from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.onedrive.workbooks.charts.title_format import WorkbookChartTitleFormat
from office365.runtime.paths.resource_path import ResourcePath


class WorkbookChartTitle(Entity):
    """Represents a chart title object of a chart."""

    @property
    def format(self) -> WorkbookChartTitleFormat:
        """The formatting of a chart title, which includes fill and font formatting."""
        return self.properties.get(
            "format",
            WorkbookChartTitleFormat(self.context, ResourcePath("format", self.resource_path)),
        )

    @property
    def overlay(self) -> Optional[bool]:
        """Gets the overlay property"""
        return self.properties.get("overlay", None)

    @property
    def text(self) -> Optional[str]:
        """Gets the text property"""
        return self.properties.get("text", None)

    @property
    def visible(self) -> Optional[bool]:
        """Gets the visible property"""
        return self.properties.get("visible", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartTitle"
