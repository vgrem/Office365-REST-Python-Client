from office365.directory.licenses.service_plan_info import ServicePlanInfo
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection


class SubscribedSku(Entity):
    """Contains information about a service SKU that a company is subscribed to."""

    @property
    def account_id(self):
        """
        :rtype: str
        """
        return self.properties.get("accountId", None)

    @property
    def sku_id(self):
        """
        The unique identifier (GUID) for the service SKU.
        :rtype: str
        """
        return self.properties.get("skuId", None)

    @property
    def service_plans(self):
        """Information about the service plans that are available with the SKU. Not nullable"""
        return self.properties.get('servicePlans', ClientValueCollection(ServicePlanInfo))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "servicePlans": self.service_plans
            }
            default_value = property_mapping.get(name, None)
        return super(SubscribedSku, self).get_property(name, default_value)
