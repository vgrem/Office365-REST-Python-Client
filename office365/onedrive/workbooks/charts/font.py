from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class WorkbookChartFont(Entity):
    """This object represents the font attributes (font name, font size, color, etc.) for a chart object."""

    @property
    def bold(self) -> Optional[bool]:
        """Gets the bold property"""
        return self.properties.get("bold", None)

    @property
    def color(self) -> Optional[str]:
        """Gets the color property"""
        return self.properties.get("color", None)

    @property
    def italic(self) -> Optional[bool]:
        """Gets the italic property"""
        return self.properties.get("italic", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def size(self) -> Optional[float]:
        """Gets the size property"""
        return self.properties.get("size", None)

    @property
    def underline(self) -> Optional[str]:
        """Gets the underline property"""
        return self.properties.get("underline", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartFont"
