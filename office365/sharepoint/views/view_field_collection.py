from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.fields.field import Field


class ViewFieldCollection(ClientObjectCollection):
    """Represents a collection of Field resources."""
    def __init__(self, context, resource_path=None):
        super(ViewFieldCollection, self).__init__(context, Field, resource_path)
