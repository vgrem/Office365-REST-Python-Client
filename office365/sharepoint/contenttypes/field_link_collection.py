from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.contenttypes.field_link import FieldLink


class FieldLinkCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(FieldLinkCollection, self).__init__(context, FieldLink, resource_path)
