from office365.entity import Entity
from office365.onedrive.workbooks.tables.column_collection import WorkbookTableColumnCollection
from office365.onedrive.workbooks.tables.row_collection import WorkbookTableRowCollection
from office365.runtime.paths.resource_path import ResourcePath


class WorkbookTable(Entity):
    """Represents an Excel table."""

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
