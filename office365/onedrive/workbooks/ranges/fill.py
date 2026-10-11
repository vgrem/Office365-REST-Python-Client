from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class WorkbookRangeFill(Entity):
    """HTML color code representing the color of the border line. Can either be of the form #RRGGBB,
    for example "FFA500", or be a named HTML color, for example "orange"."""

    @property
    def color(self) -> Optional[str]:
        """Gets or sets the width of all columns within the range. If the column widths aren't uniform,
        null will be returned."""
        return self.properties.get("color", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookRangeFill"
