from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.delegated_administration_role_assignment_snapshot import (
    DelegatedAdministrationRoleAssignmentSnapshot,
)
from office365.directory.multi_tenant_applications_to_provision_snapshot import (
    MultiTenantApplicationsToProvisionSnapshot,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class RelationshipPolicy(ClientValue):
    delegatedAdministrationRoleAssignments: ClientValueCollection[DelegatedAdministrationRoleAssignmentSnapshot] = field(
        default_factory=lambda: ClientValueCollection(DelegatedAdministrationRoleAssignmentSnapshot)
    )
    governedTenantCanTerminate: bool | None = None
    multiTenantApplicationsToProvision: ClientValueCollection[MultiTenantApplicationsToProvisionSnapshot] = field(
        default_factory=lambda: ClientValueCollection(MultiTenantApplicationsToProvisionSnapshot)
    )
    policyId: str | None = None
    version: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RelationshipPolicy"
