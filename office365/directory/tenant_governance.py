from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.governance_invitation import GovernanceInvitation
    from office365.directory.governance_relationship import GovernanceRelationship
    from office365.directory.governance_request import GovernanceRequest
    from office365.directory.related_tenant import RelatedTenant
    from office365.directory.tenant_governance_policy_template import (
        TenantGovernancePolicyTemplate,
    )
    from office365.directory.tenant_governance_setting import TenantGovernanceSetting


class TenantGovernance(Entity):
    @property
    def governance_invitations(self) -> EntityCollection[GovernanceInvitation]:
        """Gets the governanceInvitations property"""
        from office365.directory.governance_invitation import GovernanceInvitation

        return self.properties.get(
            "governanceInvitations",
            EntityCollection[GovernanceInvitation](
                self.context, GovernanceInvitation, ResourcePath("governanceInvitations", self.resource_path)
            ),
        )

    @property
    def governance_policy_templates(self) -> EntityCollection[TenantGovernancePolicyTemplate]:
        """Gets the governancePolicyTemplates property"""
        from office365.directory.tenant_governance_policy_template import (
            TenantGovernancePolicyTemplate,
        )

        return self.properties.get(
            "governancePolicyTemplates",
            EntityCollection[TenantGovernancePolicyTemplate](
                self.context,
                TenantGovernancePolicyTemplate,
                ResourcePath("governancePolicyTemplates", self.resource_path),
            ),
        )

    @property
    def governance_relationships(self) -> EntityCollection[GovernanceRelationship]:
        """Gets the governanceRelationships property"""
        from office365.directory.governance_relationship import GovernanceRelationship

        return self.properties.get(
            "governanceRelationships",
            EntityCollection[GovernanceRelationship](
                self.context, GovernanceRelationship, ResourcePath("governanceRelationships", self.resource_path)
            ),
        )

    @property
    def governance_requests(self) -> EntityCollection[GovernanceRequest]:
        """Gets the governanceRequests property"""
        from office365.directory.governance_request import GovernanceRequest

        return self.properties.get(
            "governanceRequests",
            EntityCollection[GovernanceRequest](
                self.context, GovernanceRequest, ResourcePath("governanceRequests", self.resource_path)
            ),
        )

    @property
    def related_tenants(self) -> EntityCollection[RelatedTenant]:
        """Gets the relatedTenants property"""
        from office365.directory.related_tenant import RelatedTenant

        return self.properties.get(
            "relatedTenants",
            EntityCollection[RelatedTenant](
                self.context, RelatedTenant, ResourcePath("relatedTenants", self.resource_path)
            ),
        )

    @property
    def settings(self) -> TenantGovernanceSetting:
        """Gets the settings property"""
        from office365.directory.tenant_governance_setting import (
            TenantGovernanceSetting,
        )

        return self.properties.get(
            "settings", TenantGovernanceSetting(self.context, ResourcePath("settings", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TenantGovernance"
