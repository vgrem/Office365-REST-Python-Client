from office365.entity_collection import EntityCollection
from office365.onedrive.columnDefinition import ColumnDefinition


class ColumnDefinitionCollection(EntityCollection):
    """Drive column's collection"""

    def __init__(self, context, resource_path=None):
        super(ColumnDefinitionCollection, self).__init__(context, ColumnDefinition, resource_path)
