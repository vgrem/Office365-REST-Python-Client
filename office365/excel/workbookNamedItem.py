from office365.entity import Entity
from office365.excel.workbookWorksheet import WorkbookWorksheet
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path import ResourcePath


class WorkbookNamedItem(Entity):
    """Represents a defined name for a range of cells or value. Names can be primitive named objects
    (as seen in the type below), range object, reference to a range. This object can be used to obtain range
    object associated with names."""

    @property
    def name(self):
        """The name of the object. Read-only.

        :rtype str or None
        """
        return self.properties.get('name', None)

    @property
    def comment(self):
        """Represents the comment associated with this name.

        :rtype str or None
        """
        return self.properties.get('comment', None)

    @property
    def worksheet(self):
        """Returns the worksheet on which the named item is scoped to. Available only if the item is scoped
        to the worksheet. Read-only."""
        return self.properties.get('worksheet',
                                   WorkbookWorksheet(self.context, ResourcePath("worksheet", self.resource_path)))


class WorkbookNamedItemCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookNamedItemCollection, self).__init__(context, WorkbookNamedItem, resource_path)
