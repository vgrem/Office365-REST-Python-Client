from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.features.definitions.definition import FeatureDefinition


class FeatureDefinitionCollection(BaseEntityCollection):
    """Represents a collection of feature's definitions"""

    def __init__(self, context, resource_path=None, parent=None):
        super(FeatureDefinitionCollection, self).__init__(context, FeatureDefinition, resource_path, parent)

    def get_feature_definition(self, feature_display_name, compatibility_level=None):
        """
        :param str feature_display_name:
        :param int compatibility_level:
        """
        return_type = FeatureDefinition(self.context)
        payload = {
            "featureDisplayName": feature_display_name,
            "compatibilityLevel": compatibility_level
        }
        qry = ServiceOperationQuery(self, "GetFeatureDefinition", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type
