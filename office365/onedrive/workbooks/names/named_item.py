from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.onedrive.workbooks.ranges.range import WorkbookRange
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery

if TYPE_CHECKING:
    from office365.runtime.types.json import Json


class WorkbookNamedItem(Entity):
    """Represents a defined name for a range of cells or value. Names can be primitive named objects
    (as seen in the type below), range object, reference to a range. This object can be used to obtain range
    object associated with names."""

    def range(self):
        """Returns the range object that is associated with the name. Throws an exception if the named item's type
        isn't a range."""
        return_type = WorkbookRange(self.context, ResourcePath("range", self.resource_path))
        qry = FunctionQuery(self, "range", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def name(self) -> Optional[str]:
        """The name of the object."""
        return self.properties.get("name", None)

    @property
    def comment(self) -> Optional[str]:
        """Represents the comment associated with this name."""
        return self.properties.get("comment", None)

    @property
    def scope(self) -> Optional[str]:
        """Indicates whether the name is scoped to the workbook or to a specific worksheet."""
        return self.properties.get("scope", None)

    @property
    def worksheet(self):
        """Returns the worksheet on which the named item is scoped to. Available only if the item is scoped
        to the worksheet. Read-only."""
        from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet

        return self.properties.get(
            "worksheet",
            WorkbookWorksheet(self.context, ResourcePath("worksheet", self.resource_path)),
        )

    @property
    def property_ref_name(self) -> str:
        return "name"

    @property
    def type(self) -> Optional[str]:
        """Gets the type property"""
        return self.properties.get("type", None)

    @property
    def value(self) -> Json:
        """Gets the value property"""
        from office365.runtime.types.json import Json

        return self.properties.get("value", Json())

    @property
    def visible(self) -> Optional[bool]:
        """Gets the visible property"""
        return self.properties.get("visible", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookNamedItem"
