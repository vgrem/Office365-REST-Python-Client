from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.fields.related_field import RelatedField


class RelatedFieldCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(RelatedFieldCollection, self).__init__(context, RelatedField, resource_path)
