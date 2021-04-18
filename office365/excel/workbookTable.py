from office365.entity import Entity
from office365.entity_collection import EntityCollection


class WorkbookTable(Entity):
    pass


class WorkbookTableCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookTableCollection, self).__init__(context, WorkbookTable, resource_path)
