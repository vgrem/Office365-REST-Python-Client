from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.multi_tenant_organization_join_request_record import (
        MultiTenantOrganizationJoinRequestRecord,
    )
    from office365.directory.multi_tenant_organization_member import (
        MultiTenantOrganizationMember,
    )
    from office365.directory.tenantinformation.multitenantorganizationstate import (
        MultiTenantOrganizationState,
    )


class MultiTenantOrganization(Entity):
    """
    Defines an organization with more than one instance of Microsoft Entra ID. A multitenant organization enables
    multiple tenants to collaborate like a single entity.

    There can only be one multitenant organization per active tenant. It is not possible to be part of multiple
    multitenant organizations.
    """

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def state(self) -> MultiTenantOrganizationState:
        """Gets the state property"""
        from office365.directory.tenantinformation.multitenantorganizationstate import (
            MultiTenantOrganizationState,
        )

        return self.properties.get("state", MultiTenantOrganizationState.active)

    @property
    def join_request(self) -> MultiTenantOrganizationJoinRequestRecord:
        """Gets the joinRequest property"""
        from office365.directory.multi_tenant_organization_join_request_record import (
            MultiTenantOrganizationJoinRequestRecord,
        )

        return self.properties.get(
            "joinRequest",
            MultiTenantOrganizationJoinRequestRecord(self.context, ResourcePath("joinRequest", self.resource_path)),
        )

    @property
    def tenants(self) -> EntityCollection[MultiTenantOrganizationMember]:
        """Gets the tenants property"""
        from office365.directory.multi_tenant_organization_member import (
            MultiTenantOrganizationMember,
        )

        return self.properties.get(
            "tenants",
            EntityCollection[MultiTenantOrganizationMember](
                self.context, MultiTenantOrganizationMember, ResourcePath("tenants", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MultiTenantOrganization"
