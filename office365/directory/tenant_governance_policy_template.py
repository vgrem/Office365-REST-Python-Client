from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.delegated_administration_role_assignment import (
        DelegatedAdministrationRoleAssignment,
    )
    from office365.directory.multi_tenant_applications_to_provision import (
        MultiTenantApplicationsToProvision,
    )


class TenantGovernancePolicyTemplate(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def delegated_administration_role_assignments(self) -> ClientValueCollection[DelegatedAdministrationRoleAssignment]:
        """Gets the delegatedAdministrationRoleAssignments property"""
        from office365.directory.delegated_administration_role_assignment import (
            DelegatedAdministrationRoleAssignment,
        )

        return self.properties.get(
            "delegatedAdministrationRoleAssignments",
            ClientValueCollection[DelegatedAdministrationRoleAssignment](DelegatedAdministrationRoleAssignment),
        )

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def governed_tenant_can_terminate(self) -> Optional[bool]:
        """Gets the governedTenantCanTerminate property"""
        return self.properties.get("governedTenantCanTerminate", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def multi_tenant_applications_to_provision(self) -> ClientValueCollection[MultiTenantApplicationsToProvision]:
        """Gets the multiTenantApplicationsToProvision property"""
        from office365.directory.multi_tenant_applications_to_provision import (
            MultiTenantApplicationsToProvision,
        )

        return self.properties.get(
            "multiTenantApplicationsToProvision",
            ClientValueCollection[MultiTenantApplicationsToProvision](MultiTenantApplicationsToProvision),
        )

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TenantGovernancePolicyTemplate"
