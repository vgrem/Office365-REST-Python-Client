from office365.graph.onedrive.columnDefinition import ColumnDefinition
from office365.runtime.client_object_collection import ClientObjectCollection


class ColumnDefinitionCollection(ClientObjectCollection):
    """Drive column's collection"""

    def __init__(self, context, resource_path=None):
        super(ColumnDefinitionCollection, self).__init__(context, ColumnDefinition, resource_path)
