from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.applications.templateapplicationlevel import (
        TemplateApplicationLevel,
    )
    from office365.directory.policies.crosstenant.user_sync_inbound import (
        CrossTenantUserSyncInbound,
    )


class MultiTenantOrganizationIdentitySyncPolicyTemplate(Entity):
    @property
    def template_application_level(self) -> TemplateApplicationLevel:
        """Gets the templateApplicationLevel property"""
        from office365.directory.applications.templateapplicationlevel import (
            TemplateApplicationLevel,
        )

        return self.properties.get("templateApplicationLevel", TemplateApplicationLevel.none)

    @property
    def user_sync_inbound(self) -> CrossTenantUserSyncInbound:
        """Gets the userSyncInbound property"""
        from office365.directory.policies.crosstenant.user_sync_inbound import (
            CrossTenantUserSyncInbound,
        )

        return self.properties.get("userSyncInbound", CrossTenantUserSyncInbound())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MultiTenantOrganizationIdentitySyncPolicyTemplate"
