from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.fields.related_field import RelatedField


class RelatedFieldCollection(BaseEntityCollection):
    """Represents a collection of RelatedField resources."""

    def __init__(self, context, resource_path=None):
        super(RelatedFieldCollection, self).__init__(context, RelatedField, resource_path)

    def get_by_field_id(self, _id):
        """Gets the RelatedField with the specified ID."""
        return RelatedField(self.context, ServiceOperationPath("GetByFieldId", [_id], self.resource_path))
