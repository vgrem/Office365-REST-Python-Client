from office365.directory.licenses.service_plan_info import ServicePlanInfo
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection


class LicenseDetails(Entity):
    """Contains information about a license assigned to a user."""

    @property
    def service_plans(self):
        """
        Information about the service plans assigned with the license. Read-only, Not nullable
        """
        return self.properties.get('servicePlans', ClientValueCollection(ServicePlanInfo))

    @property
    def sku_id(self):
        """
        Unique identifier (GUID) for the service SKU. Equal to the skuId property on the related SubscribedSku object.
        Read-only
        :rtype: str or None
        """
        return self.properties.get('skuId', None)

    @property
    def sku_part_number(self):
        """
        Unique SKU display name. Equal to the skuPartNumber on the related SubscribedSku object;
        for example: "AAD_Premium". Read-only
        :rtype: str or None
        """
        return self.properties.get('skuPartNumber', None)
