from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.licenses.service_plan_info import ServicePlanInfo


class CompanySubscription(Entity):
    """Represents a commercial subscription for a tenant. Use the values of skuId and serviceStatus > servicePlanId
    to assign licenses to unassigned users and groups through the user: assignLicense and group: assignLicense
    APIs respectively."""

    @property
    def commerce_subscription_id(self) -> Optional[str]:
        """Gets the commerceSubscriptionId property"""
        return self.properties.get("commerceSubscriptionId", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def is_trial(self) -> Optional[bool]:
        """Gets the isTrial property"""
        return self.properties.get("isTrial", None)

    @property
    def next_lifecycle_date_time(self) -> Optional[datetime]:
        """Gets the nextLifecycleDateTime property"""
        return self.properties.get("nextLifecycleDateTime", datetime.min)

    @property
    def owner_id(self) -> Optional[str]:
        """Gets the ownerId property"""
        return self.properties.get("ownerId", None)

    @property
    def owner_tenant_id(self) -> Optional[str]:
        """Gets the ownerTenantId property"""
        return self.properties.get("ownerTenantId", None)

    @property
    def owner_type(self) -> Optional[str]:
        """Gets the ownerType property"""
        return self.properties.get("ownerType", None)

    @property
    def service_status(self) -> ClientValueCollection[ServicePlanInfo]:
        """Gets the serviceStatus property"""
        from office365.directory.licenses.service_plan_info import ServicePlanInfo

        return self.properties.get("serviceStatus", ClientValueCollection[ServicePlanInfo](ServicePlanInfo))

    @property
    def sku_id(self) -> Optional[str]:
        """Gets the skuId property"""
        return self.properties.get("skuId", None)

    @property
    def sku_part_number(self) -> Optional[str]:
        """Gets the skuPartNumber property"""
        return self.properties.get("skuPartNumber", None)

    @property
    def status(self) -> Optional[str]:
        """Gets the status property"""
        return self.properties.get("status", None)

    @property
    def total_licenses(self) -> Optional[int]:
        """Gets the totalLicenses property"""
        return self.properties.get("totalLicenses", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CompanySubscription"
