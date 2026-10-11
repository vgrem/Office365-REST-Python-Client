from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class ResellerDelegatedAdminRelationship(Entity):
    @property
    def indirect_provider_tenant_id(self) -> Optional[str]:
        """Gets the indirectProviderTenantId property"""
        return self.properties.get("indirectProviderTenantId", None)

    @property
    def is_partner_consent_pending(self) -> Optional[bool]:
        """Gets the isPartnerConsentPending property"""
        return self.properties.get("isPartnerConsentPending", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ResellerDelegatedAdminRelationship"
