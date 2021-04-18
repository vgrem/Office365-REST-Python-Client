from office365.entity import Entity
from office365.runtime.client_object_collection import ClientObjectCollection


class WorkbookWorksheet(Entity):
    """
    An Excel worksheet is a grid of cells. It can contain data, tables, charts, etc
    """

    @property
    def name(self):
        """
        The display name of the worksheet.
        :rtype: str or None
        """
        return self.properties.get('name', None)


class WorkbookWorksheetCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookWorksheetCollection, self).__init__(context, WorkbookWorksheet, resource_path)
