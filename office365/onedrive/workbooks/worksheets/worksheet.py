from __future__ import annotations

from typing import Optional

from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.charts.chart import WorkbookChart
from office365.onedrive.workbooks.names.named_item import WorkbookNamedItem
from office365.onedrive.workbooks.ranges.range import WorkbookRange
from office365.onedrive.workbooks.tables.collection import WorkbookTableCollection
from office365.onedrive.workbooks.tables.pivot_table_collection import (
    WorkbookPivotTableCollection,
)
from office365.onedrive.workbooks.worksheets.protection import (
    WorkbookWorksheetProtection,
)
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.types.odata_property import odata


class WorkbookWorksheet(Entity):
    """
    An Excel worksheet is a grid of cells. It can contain data, tables, charts, etc
    """

    def __repr__(self):
        return self.name or self.entity_type_name

    def __str__(self):
        return self.name or self.entity_type_name

    @require_permission(delegated=["Files.ReadWrite"], application=["Files.ReadWrite"])
    def cell(self, row: int, column: int) -> WorkbookRange:
        """Gets the range object containing the single cell based on row and column numbers.
        The cell can be outside the bounds of its parent range, so long as it's stays within the worksheet grid.

        Args:
            row (int): Row number of the cell to be retrieved. Zero-indexed.
            column (int): Column number of the cell to be retrieved. Zero-indexed.
        """
        return_type = WorkbookRange(self.context, ResourcePath("range", self.resource_path))
        params = {"row": row, "column": column}
        qry = FunctionQuery(self, "cell", method_params=params, return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["Files.ReadWrite"], application=["Files.ReadWrite"])
    def range(self, address=None):
        """Gets the range object specified by the address or name."""
        return_type = WorkbookRange(
            self.context, ServiceOperationPath("range", {"address": address}, self.resource_path)
        )
        qry = FunctionQuery(self, "range", method_params={"address": address}, return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["Files.ReadWrite"], application=["Files.ReadWrite"])
    def used_range(self, values_only: bool = False) -> WorkbookRange:
        """Return the used range of the given range object.

        Args:
            values_only (bool): Optional. Considers only cells with values as used cells.
        """
        return_type = WorkbookRange(self.context)
        params = {"valuesOnly": values_only}
        qry = FunctionQuery(self, "usedRange", params, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def charts(self) -> EntityCollection[WorkbookChart]:
        """Returns collection of charts that are part of the worksheet"""
        return self.properties.get(
            "charts",
            EntityCollection(self.context, WorkbookChart, ResourcePath("charts", self.resource_path)),
        )

    @property
    def name(self) -> Optional[str]:
        """The display name of the worksheet."""
        return self.properties.get("name", None)

    @property
    def names(self) -> EntityCollection[WorkbookNamedItem]:
        """Returns collection of names that are associated with the worksheet"""
        return self.properties.get(
            "names",
            EntityCollection(
                self.context,
                WorkbookNamedItem,
                ResourcePath("names", self.resource_path),
            ),
        )

    @property
    def tables(self) -> WorkbookTableCollection:
        """Collection of tables that are part of the worksheet."""
        return self.properties.get(
            "tables",
            WorkbookTableCollection(self.context, ResourcePath("tables", self.resource_path)),
        )

    @odata(name="pivotTables")
    @property
    def pivot_tables(self) -> WorkbookPivotTableCollection:
        """Collection of PivotTables that are part of the worksheet."""
        return self.properties.get(
            "pivotTables",
            WorkbookPivotTableCollection(
                self.context,
                ResourcePath("pivotTables", self.resource_path),
            ),
        )

    @property
    def protection(self) -> WorkbookWorksheetProtection:
        """Returns sheet protection object for a worksheet."""
        return self.properties.get(
            "protection",
            WorkbookWorksheetProtection(self.context, ResourcePath("protection", self.resource_path)),
        )

    @property
    def position(self) -> Optional[int]:
        """Gets the position property"""
        return self.properties.get("position", None)

    @property
    def visibility(self) -> Optional[str]:
        """Gets the visibility property"""
        return self.properties.get("visibility", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookWorksheet"
