from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.runtime.types.json import Json


class WorkbookRangeView(Entity):
    """Represents a set of visible cells of the parent range."""

    @property
    def cell_addresses(self) -> Optional[dict]:
        """The cell addresses."""
        return self.properties.get("cellAddresses", None)

    @property
    def column_count(self) -> Optional[int]:
        """The number of visible columns."""
        return self.properties.get("columnCount", None)

    @property
    def rows(self) -> EntityCollection[WorkbookRangeView]:
        """Represents a collection of range views associated with the range."""
        return self.properties.get(
            "rows",
            EntityCollection(
                self.context,
                WorkbookRangeView,
                ResourcePath("rows", self.resource_path),
            ),
        )

    @property
    def formulas(self) -> Json:
        """Gets the formulas property"""
        from office365.runtime.types.json import Json

        return self.properties.get("formulas", Json())

    @property
    def formulas_local(self) -> Json:
        """Gets the formulasLocal property"""
        from office365.runtime.types.json import Json

        return self.properties.get("formulasLocal", Json())

    @property
    def formulas_r1_c1(self) -> Json:
        """Gets the formulasR1C1 property"""
        from office365.runtime.types.json import Json

        return self.properties.get("formulasR1C1", Json())

    @property
    def index(self) -> Optional[int]:
        """Gets the index property"""
        return self.properties.get("index", None)

    @property
    def number_format(self) -> Json:
        """Gets the numberFormat property"""
        from office365.runtime.types.json import Json

        return self.properties.get("numberFormat", Json())

    @property
    def row_count(self) -> Optional[int]:
        """Gets the rowCount property"""
        return self.properties.get("rowCount", None)

    @property
    def text(self) -> Json:
        """Gets the text property"""
        from office365.runtime.types.json import Json

        return self.properties.get("text", Json())

    @property
    def values(self) -> Json:
        """Gets the values property"""
        from office365.runtime.types.json import Json

        return self.properties.get("values", Json())

    @property
    def value_types(self) -> Json:
        """Gets the valueTypes property"""
        from office365.runtime.types.json import Json

        return self.properties.get("valueTypes", Json())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookRangeView"
