from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.tenantinformation.multitenantorganizationmemberrole import (
        MultiTenantOrganizationMemberRole,
    )
    from office365.directory.tenantinformation.multitenantorganizationmemberstate import (
        MultiTenantOrganizationMemberState,
    )
    from office365.security.audit.multi_tenant_organization_join_request_transition_details import (
        MultiTenantOrganizationJoinRequestTransitionDetails,
    )


class MultiTenantOrganizationJoinRequestRecord(Entity):
    @property
    def added_by_tenant_id(self) -> Optional[str]:
        """Gets the addedByTenantId property"""
        return self.properties.get("addedByTenantId", None)

    @property
    def member_state(self) -> MultiTenantOrganizationMemberState:
        """Gets the memberState property"""
        from office365.directory.tenantinformation.multitenantorganizationmemberstate import (
            MultiTenantOrganizationMemberState,
        )

        return self.properties.get("memberState", MultiTenantOrganizationMemberState.pending)

    @property
    def role(self) -> MultiTenantOrganizationMemberRole:
        """Gets the role property"""
        from office365.directory.tenantinformation.multitenantorganizationmemberrole import (
            MultiTenantOrganizationMemberRole,
        )

        return self.properties.get("role", MultiTenantOrganizationMemberRole.owner)

    @property
    def transition_details(self) -> MultiTenantOrganizationJoinRequestTransitionDetails:
        """Gets the transitionDetails property"""
        from office365.security.audit.multi_tenant_organization_join_request_transition_details import (
            MultiTenantOrganizationJoinRequestTransitionDetails,
        )

        return self.properties.get("transitionDetails", MultiTenantOrganizationJoinRequestTransitionDetails())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MultiTenantOrganizationJoinRequestRecord"
