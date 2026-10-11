from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.tenantinformation.multitenantorganizationmemberrole import (
        MultiTenantOrganizationMemberRole,
    )
    from office365.directory.tenantinformation.multitenantorganizationmemberstate import (
        MultiTenantOrganizationMemberState,
    )
    from office365.security.audit.multi_tenant_organization_member_transition_details import (
        MultiTenantOrganizationMemberTransitionDetails,
    )


class MultiTenantOrganizationMember(Entity):
    @property
    def added_by_tenant_id(self) -> Optional[UUID]:
        """Gets the addedByTenantId property"""
        return self.properties.get("addedByTenantId", None)

    @property
    def added_date_time(self) -> Optional[datetime]:
        """Gets the addedDateTime property"""
        return self.properties.get("addedDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def joined_date_time(self) -> Optional[datetime]:
        """Gets the joinedDateTime property"""
        return self.properties.get("joinedDateTime", datetime.min)

    @property
    def role(self) -> MultiTenantOrganizationMemberRole:
        """Gets the role property"""
        from office365.directory.tenantinformation.multitenantorganizationmemberrole import (
            MultiTenantOrganizationMemberRole,
        )

        return self.properties.get("role", MultiTenantOrganizationMemberRole.owner)

    @property
    def state(self) -> MultiTenantOrganizationMemberState:
        """Gets the state property"""
        from office365.directory.tenantinformation.multitenantorganizationmemberstate import (
            MultiTenantOrganizationMemberState,
        )

        return self.properties.get("state", MultiTenantOrganizationMemberState.pending)

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def transition_details(self) -> MultiTenantOrganizationMemberTransitionDetails:
        """Gets the transitionDetails property"""
        from office365.security.audit.multi_tenant_organization_member_transition_details import (
            MultiTenantOrganizationMemberTransitionDetails,
        )

        return self.properties.get("transitionDetails", MultiTenantOrganizationMemberTransitionDetails())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MultiTenantOrganizationMember"
