from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.contenttypes.field_link import FieldLink


class FieldLinkCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(FieldLinkCollection, self).__init__(context, FieldLink, resource_path)
