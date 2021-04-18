from office365.entity import Entity
from office365.excel.workbookFunctions import WorkbookFunctions
from office365.excel.workbookNamedItem import WorkbookNamedItemCollection
from office365.excel.workbookTable import WorkbookTableCollection
from office365.excel.workbookWorksheet import WorkbookWorksheetCollection
from office365.runtime.resource_path import ResourcePath


class Workbook(Entity):
    """The top-level object that contains related workbook objects such as worksheets, tables, and ranges."""

    @property
    def functions(self):
        return self.properties.get('functions',
                                   WorkbookFunctions(self.context, ResourcePath("functions", self.resource_path)))

    @property
    def tables(self):
        """Represents a collection of tables associated with the workbook. Read-only."""
        return self.properties.get('tables',
                                   WorkbookTableCollection(self.context, ResourcePath("tables", self.resource_path)))

    @property
    def names(self):
        """Represents a collection of workbook scoped named items (named ranges and constants). Read-only."""
        return self.properties.get('names',
                                   WorkbookNamedItemCollection(self.context, ResourcePath("names", self.resource_path)))

    @property
    def worksheets(self):
        """Represents a collection of worksheets associated with the workbook. Read-only."""
        return self.properties.get('worksheets',
                                   WorkbookWorksheetCollection(self.context,
                                                               ResourcePath("worksheets", self.resource_path)))
