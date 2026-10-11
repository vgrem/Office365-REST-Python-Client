from __future__ import annotations

from dataclasses import dataclass

from office365.directory.tenantinformation.multitenantorganizationmemberprocessingstatus import (
    MultiTenantOrganizationMemberProcessingStatus,
)
from office365.directory.tenantinformation.multitenantorganizationmemberrole import MultiTenantOrganizationMemberRole
from office365.directory.tenantinformation.multitenantorganizationmemberstate import MultiTenantOrganizationMemberState
from office365.runtime.client_value import ClientValue


@dataclass
class MultiTenantOrganizationMemberTransitionDetails(ClientValue):
    desiredRole: MultiTenantOrganizationMemberRole = MultiTenantOrganizationMemberRole.owner
    desiredState: MultiTenantOrganizationMemberState = MultiTenantOrganizationMemberState.pending
    details: str | None = None
    status: MultiTenantOrganizationMemberProcessingStatus = MultiTenantOrganizationMemberProcessingStatus.notStarted

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MultiTenantOrganizationMemberTransitionDetails"
