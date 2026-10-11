from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.administrative_unit import AdministrativeUnit
from office365.directory.certificates.public_key_infrastructure_root import (
    PublicKeyInfrastructureRoot,
)
from office365.directory.custom_security_attribute_definition import (
    CustomSecurityAttributeDefinition,
)
from office365.directory.device_local_credential_info import DeviceLocalCredentialInfo
from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.subscriptions.company import CompanySubscription
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.common.attribute_set import AttributeSet
    from office365.directory.identities.providers.base import IdentityProviderBase
    from office365.directory.on_premises_directory_synchronization import (
        OnPremisesDirectorySynchronization,
    )
    from office365.directory.recovery.recovery import Recovery
    from office365.directory.remote_tenant_group import RemoteTenantGroup
    from office365.directory.tenant_governance import TenantGovernance


class Directory(Entity):
    """Represents a deleted item in the directory. When an item is deleted, it is added to the deleted items
    "container". Deleted items will remain available to restore for up to 30 days. After 30 days, the items are
    permanently deleted."""

    @odata(name="deviceLocalCredentials")
    @property
    def device_local_credentials(self) -> EntityCollection[DeviceLocalCredentialInfo]:
        """Conceptual container for user and group directory objects."""
        return self.properties.get(
            "deviceLocalCredentials",
            EntityCollection(
                self.context,
                DeviceLocalCredentialInfo,
                ResourcePath("deviceLocalCredentials", self.resource_path),
            ),
        )

    @odata(name="administrativeUnits")
    @property
    def administrative_units(self):
        """Conceptual container for user and group directory objects."""
        return self.properties.get(
            "administrativeUnits",
            EntityCollection(
                self.context,
                AdministrativeUnit,
                ResourcePath("administrativeUnits", self.resource_path),
            ),
        )

    @odata(name="customSecurityAttributeDefinitions")
    @property
    def custom_security_attribute_definitions(self):
        """Conceptual container for customSecurityAttributeDefinition objects and their properties."""
        return self.properties.get(
            "customSecurityAttributeDefinitions",
            EntityCollection(
                self.context,
                CustomSecurityAttributeDefinition,
                ResourcePath("customSecurityAttributeDefinitions", self.resource_path),
            ),
        )

    @odata(name="publicKeyInfrastructure")
    @property
    def public_key_infrastructure(self):
        """"""
        return self.properties.get(
            "publicKeyInfrastructure",
            PublicKeyInfrastructureRoot(
                self.context,
                ResourcePath("publicKeyInfrastructure", self.resource_path),
            ),
        )

    @property
    def subscriptions(self) -> EntityCollection[CompanySubscription]:
        """List of commercial subscriptions that an organization acquired."""
        return self.properties.get(
            "subscriptions",
            EntityCollection(
                self.context,
                CompanySubscription,
                ResourcePath("subscriptions", self.resource_path),
            ),
        )

    def deleted_items(self, entity_type=None) -> DirectoryObjectCollection:
        """Recently deleted items. Read-only. Nullable."""
        if entity_type:
            return self.properties.get(
                "deletedItems",
                DirectoryObjectCollection(
                    self.context,
                    ResourcePath(entity_type, ResourcePath("deletedItems", self.resource_path)),
                ),
            )
        else:
            return self.properties.get(
                "deletedItems",
                DirectoryObjectCollection(self.context, ResourcePath("deletedItems", self.resource_path)),
            )

    @property
    def deleted_groups(self):
        """Recently deleted groups"""
        return self.deleted_items("microsoft.graph.group")

    @property
    def deleted_teams(self):
        """Recently deleted groups"""
        return self.deleted_items("microsoft.graph.group").filter("resourceProvisioningOptions/Any(x:x eq 'Team')")

    @property
    def deleted_users(self):
        """Recently deleted users"""
        return self.deleted_items("microsoft.graph.user")

    @property
    def deleted_applications(self):
        """Recently deleted applications"""
        return self.deleted_items("microsoft.graph.application")

    @property
    def deleted_service_principals(self):
        """Recently deleted service Principals"""
        return self.deleted_items("microsoft.graph.servicePrincipal")

    @property
    def attribute_sets(self) -> EntityCollection[AttributeSet]:
        """Gets the attributeSets property"""
        from office365.common.attribute_set import AttributeSet

        return self.properties.get(
            "attributeSets",
            EntityCollection[AttributeSet](
                self.context, AttributeSet, ResourcePath("attributeSets", self.resource_path)
            ),
        )

    @property
    def federation_configurations(self) -> EntityCollection[IdentityProviderBase]:
        """Gets the federationConfigurations property"""
        from office365.directory.identities.providers.base import IdentityProviderBase

        return self.properties.get(
            "federationConfigurations",
            EntityCollection[IdentityProviderBase](
                self.context, IdentityProviderBase, ResourcePath("federationConfigurations", self.resource_path)
            ),
        )

    @property
    def on_premises_synchronization(self) -> EntityCollection[OnPremisesDirectorySynchronization]:
        """Gets the onPremisesSynchronization property"""
        from office365.directory.on_premises_directory_synchronization import (
            OnPremisesDirectorySynchronization,
        )

        return self.properties.get(
            "onPremisesSynchronization",
            EntityCollection[OnPremisesDirectorySynchronization](
                self.context,
                OnPremisesDirectorySynchronization,
                ResourcePath("onPremisesSynchronization", self.resource_path),
            ),
        )

    @property
    def remote_tenant_groups(self) -> EntityCollection[RemoteTenantGroup]:
        """Gets the remoteTenantGroups property"""
        from office365.directory.remote_tenant_group import RemoteTenantGroup

        return self.properties.get(
            "remoteTenantGroups",
            EntityCollection[RemoteTenantGroup](
                self.context, RemoteTenantGroup, ResourcePath("remoteTenantGroups", self.resource_path)
            ),
        )

    @property
    def recovery(self) -> Recovery:
        """Gets the recovery property"""
        from office365.directory.recovery.recovery import Recovery

        return self.properties.get("recovery", Recovery(self.context, ResourcePath("recovery", self.resource_path)))

    @property
    def tenant_governance(self) -> TenantGovernance:
        """Gets the tenantGovernance property"""
        from office365.directory.tenant_governance import TenantGovernance

        return self.properties.get(
            "tenantGovernance", TenantGovernance(self.context, ResourcePath("tenantGovernance", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Directory"
