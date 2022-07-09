from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.tables.column import WorkbookTableColumn


class WorkbookTableColumnCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookTableColumnCollection, self).__init__(context, WorkbookTableColumn, resource_path)


