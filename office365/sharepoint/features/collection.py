from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.features.feature import Feature


class FeatureCollection(BaseEntityCollection):
    """Represents a collection of Feature resources."""

    def __init__(self, context, resource_path=None, parent=None):
        super(FeatureCollection, self).__init__(context, Feature, resource_path, parent)
