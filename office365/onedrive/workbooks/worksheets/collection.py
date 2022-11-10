from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet


class WorkbookWorksheetCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookWorksheetCollection, self).__init__(context, WorkbookWorksheet, resource_path)

    def __getitem__(self, id_or_name):
        """
        :rtype: WorkbookWorksheet
        """
        return super(WorkbookWorksheetCollection, self).__getitem__(id_or_name)
