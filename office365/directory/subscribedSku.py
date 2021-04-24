from office365.directory.servicePlanInfo import ServicePlanInfo
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection


class SubscribedSku(Entity):
    """Contains information about a service SKU that a company is subscribed to."""

    @property
    def servicePlans(self):
        """Information about the service plans that are available with the SKU. Not nullable"""
        return self.properties.get('servicePlans',
                                   ClientValueCollection(ServicePlanInfo))


class SubscribedSkuCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(SubscribedSkuCollection, self).__init__(context, SubscribedSku, resource_path)
