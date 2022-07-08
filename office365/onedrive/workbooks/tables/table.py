from office365.entity import Entity
from office365.onedrive.workbooks.tables.row_collection import WorkbookTableRowCollection
from office365.runtime.paths.resource_path import ResourcePath


class WorkbookTable(Entity):
    """Represents an Excel table."""

    @property
    def tables(self):
        """
        Represents a collection of all the rows in the table.
        """
        return self.properties.get('rows',
                                   WorkbookTableRowCollection(self.context, ResourcePath("rows", self.resource_path)))
