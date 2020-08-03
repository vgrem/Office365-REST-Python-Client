from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.fields.related_field import RelatedField


class RelatedFieldCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(RelatedFieldCollection, self).__init__(context, RelatedField, resource_path)
