from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.management.virtualendpoint.cloudpcs.onpremisesconnectionstatus import (
        CloudPcOnPremisesConnectionStatus,
    )
    from office365.intune.devices.management.virtualendpoint.cloudpcs.onpremisesconnectionstatusdetail import (
        CloudPcOnPremisesConnectionStatusDetail,
    )
    from office365.intune.devices.management.virtualendpoint.cloudpcs.onpremisesconnectiontype import (
        CloudPcOnPremisesConnectionType,
    )


class CloudPcOnPremisesConnection(Entity):
    @property
    def ad_domain_name(self) -> Optional[str]:
        """Gets the adDomainName property"""
        return self.properties.get("adDomainName", None)

    @property
    def ad_domain_password(self) -> Optional[str]:
        """Gets the adDomainPassword property"""
        return self.properties.get("adDomainPassword", None)

    @property
    def ad_domain_username(self) -> Optional[str]:
        """Gets the adDomainUsername property"""
        return self.properties.get("adDomainUsername", None)

    @property
    def alternate_resource_url(self) -> Optional[str]:
        """Gets the alternateResourceUrl property"""
        return self.properties.get("alternateResourceUrl", None)

    @property
    def connection_type(self) -> CloudPcOnPremisesConnectionType:
        """Gets the connectionType property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.onpremisesconnectiontype import (
            CloudPcOnPremisesConnectionType,
        )

        return self.properties.get("connectionType", CloudPcOnPremisesConnectionType.hybridAzureADJoin)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def health_check_paused(self) -> Optional[bool]:
        """Gets the healthCheckPaused property"""
        return self.properties.get("healthCheckPaused", None)

    @property
    def health_check_status(self) -> CloudPcOnPremisesConnectionStatus:
        """Gets the healthCheckStatus property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.onpremisesconnectionstatus import (
            CloudPcOnPremisesConnectionStatus,
        )

        return self.properties.get("healthCheckStatus", CloudPcOnPremisesConnectionStatus.pending)

    @property
    def health_check_status_detail(self) -> CloudPcOnPremisesConnectionStatusDetail:
        """Gets the healthCheckStatusDetail property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.onpremisesconnectionstatusdetail import (
            CloudPcOnPremisesConnectionStatusDetail,
        )

        return self.properties.get("healthCheckStatusDetail", CloudPcOnPremisesConnectionStatusDetail())

    @property
    def in_use(self) -> Optional[bool]:
        """Gets the inUse property"""
        return self.properties.get("inUse", None)

    @property
    def in_use_by_cloud_pc(self) -> Optional[bool]:
        """Gets the inUseByCloudPc property"""
        return self.properties.get("inUseByCloudPc", None)

    @property
    def organizational_unit(self) -> Optional[str]:
        """Gets the organizationalUnit property"""
        return self.properties.get("organizationalUnit", None)

    @property
    def resource_group_id(self) -> Optional[str]:
        """Gets the resourceGroupId property"""
        return self.properties.get("resourceGroupId", None)

    @property
    def scope_ids(self) -> StringCollection:
        """Gets the scopeIds property"""
        return self.properties.get("scopeIds", StringCollection())

    @property
    def subnet_id(self) -> Optional[str]:
        """Gets the subnetId property"""
        return self.properties.get("subnetId", None)

    @property
    def subscription_id(self) -> Optional[str]:
        """Gets the subscriptionId property"""
        return self.properties.get("subscriptionId", None)

    @property
    def subscription_name(self) -> Optional[str]:
        """Gets the subscriptionName property"""
        return self.properties.get("subscriptionName", None)

    @property
    def virtual_network_id(self) -> Optional[str]:
        """Gets the virtualNetworkId property"""
        return self.properties.get("virtualNetworkId", None)

    @property
    def virtual_network_location(self) -> Optional[str]:
        """Gets the virtualNetworkLocation property"""
        return self.properties.get("virtualNetworkLocation", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudPcOnPremisesConnection"
