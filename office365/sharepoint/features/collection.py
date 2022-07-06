from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.features.feature import Feature


class FeatureCollection(BaseEntityCollection):
    """Represents a collection of Feature resources."""

    def __init__(self, context, resource_path=None, parent=None):
        super(FeatureCollection, self).__init__(context, Feature, resource_path, parent)

    def add(self, feature_id, force, featdef_scope):
        """
        Adds the feature to the collection of activated features and returns the added feature.

        :param str feature_id: The feature identifier of the feature to be added.
        :param bool force: Specifies whether to continue with the operation even if there are errors.
        :param int featdef_scope: The feature scope for this feature.
        """
        return_type = Feature(self.context)
        payload = {
            "featureId": feature_id,
            "force": force,
            "featdefScope": featdef_scope
        }
        self.add_child(return_type)
        qry = ServiceOperationQuery(self, "Add", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_by_id(self, feature_id):
        """Returns the feature for the given feature identifier. Returns NULL if no feature is available for the given
            feature identifier.

        :param str feature_id:  The feature identifier of the feature to be returned.
        """
        return Feature(self.context, ServiceOperationPath("GetById", [feature_id], self.resource_path))
