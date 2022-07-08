from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.tables.row import WorkbookTableRow


class WorkbookTableRowCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookTableRowCollection, self).__init__(context, WorkbookTableRow, resource_path)
