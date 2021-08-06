from office365.directory.licenses.service_plan_info import ServicePlanInfo
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection


class SubscribedSku(Entity):
    """Contains information about a service SKU that a company is subscribed to."""

    @property
    def service_plans(self):
        """Information about the service plans that are available with the SKU. Not nullable"""
        return self.properties.get('servicePlans', ClientValueCollection(ServicePlanInfo))
