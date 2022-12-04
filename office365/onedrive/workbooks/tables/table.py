from office365.entity import Entity
from office365.onedrive.workbooks.ranges.range import WorkbookRange
from office365.onedrive.workbooks.tables.columns.collection import WorkbookTableColumnCollection
from office365.onedrive.workbooks.tables.rows.collection import WorkbookTableRowCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery


class WorkbookTable(Entity):
    """Represents an Excel table."""

    def data_body_range(self):
        """Gets the range object associated with the data body of the table."""
        return_type = WorkbookRange(self.context)
        qry = FunctionQuery(self, "dataBodyRange", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    def range(self):
        """Get the range object associated with the entire table."""
        return_type = WorkbookRange(self.context)
        qry = FunctionQuery(self, "range", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    def total_row_range(self):
        """Gets the range object associated with totals row of the table."""
        return_type = WorkbookRange(self.context)
        qry = FunctionQuery(self, "totalRowRange", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    def clear_filters(self):
        """Clears all the filters currently applied on the table."""
        qry = ServiceOperationQuery(self, "clearFilters")
        self.context.add_query(qry)
        return self

    def reapply_filters(self):
        """Reapplies all the filters currently on the table."""
        qry = ServiceOperationQuery(self, "reapplyFilters")
        self.context.add_query(qry)
        return self

    @property
    def name(self):
        """Name of the table."""
        return self.properties.get("name", str())

    @property
    def columns(self):
        """
        Represents a collection of all the columns in the table.
        """
        return self.properties.get('columns',
                                   WorkbookTableColumnCollection(self.context,
                                                                 ResourcePath("columns", self.resource_path)))

    @property
    def rows(self):
        """
        Represents a collection of all the rows in the table.
        """
        return self.properties.get('rows',
                                   WorkbookTableRowCollection(self.context, ResourcePath("rows", self.resource_path)))

    @property
    def worksheet(self):
        """The worksheet containing the current table. """
        from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet
        return self.properties.get('worksheet',
                                   WorkbookWorksheet(self.context, ResourcePath("worksheet", self.resource_path)))
