from office365.entity import Entity
from office365.onedrive.workbookNamedItem import WorkbookNamedItemCollection
from office365.onedrive.workbookWorksheet import WorkbookWorksheetCollection
from office365.runtime.resource_path import ResourcePath


class Workbook(Entity):
    """The top-level object that contains related workbook objects such as worksheets, tables, and ranges."""

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
