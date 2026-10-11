from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class BillingMetricsBase(Entity):
    @property
    def foreign_associated_tenant_billing_management_active_count(self) -> Optional[float]:
        """Gets the foreignAssociatedTenantBillingManagementActiveCount property"""
        return self.properties.get("foreignAssociatedTenantBillingManagementActiveCount", None)

    @property
    def foreign_associated_tenant_count(self) -> Optional[float]:
        """Gets the foreignAssociatedTenantCount property"""
        return self.properties.get("foreignAssociatedTenantCount", None)

    @property
    def foreign_associated_tenant_provisioning_active_count(self) -> Optional[float]:
        """Gets the foreignAssociatedTenantProvisioningActiveCount property"""
        return self.properties.get("foreignAssociatedTenantProvisioningActiveCount", None)

    @property
    def local_associated_tenant_billing_management_active_count(self) -> Optional[float]:
        """Gets the localAssociatedTenantBillingManagementActiveCount property"""
        return self.properties.get("localAssociatedTenantBillingManagementActiveCount", None)

    @property
    def local_associated_tenant_count(self) -> Optional[float]:
        """Gets the localAssociatedTenantCount property"""
        return self.properties.get("localAssociatedTenantCount", None)

    @property
    def local_associated_tenant_ids(self) -> StringCollection:
        """Gets the localAssociatedTenantIds property"""
        return self.properties.get("localAssociatedTenantIds", StringCollection())

    @property
    def local_associated_tenant_provisioning_active_count(self) -> Optional[float]:
        """Gets the localAssociatedTenantProvisioningActiveCount property"""
        return self.properties.get("localAssociatedTenantProvisioningActiveCount", None)

    @property
    def watermark_date_time(self) -> Optional[datetime]:
        """Gets the watermarkDateTime property"""
        return self.properties.get("watermarkDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BillingMetricsBase"
