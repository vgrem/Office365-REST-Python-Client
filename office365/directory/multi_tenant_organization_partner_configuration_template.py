from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.applications.templateapplicationlevel import (
        TemplateApplicationLevel,
    )
    from office365.directory.policies.crosstenant.b2_b_setting import (
        CrossTenantAccessPolicyB2BSetting,
    )
    from office365.directory.policies.crosstenant.inbound_trust import (
        CrossTenantAccessPolicyInboundTrust,
    )
    from office365.directory.policies.inbound_outbound_policy_configuration import (
        InboundOutboundPolicyConfiguration,
    )


class MultiTenantOrganizationPartnerConfigurationTemplate(Entity):
    @property
    def automatic_user_consent_settings(self) -> InboundOutboundPolicyConfiguration:
        """Gets the automaticUserConsentSettings property"""
        from office365.directory.policies.inbound_outbound_policy_configuration import (
            InboundOutboundPolicyConfiguration,
        )

        return self.properties.get("automaticUserConsentSettings", InboundOutboundPolicyConfiguration())

    @property
    def b2b_collaboration_inbound(self) -> CrossTenantAccessPolicyB2BSetting:
        """Gets the b2bCollaborationInbound property"""
        from office365.directory.policies.crosstenant.b2_b_setting import (
            CrossTenantAccessPolicyB2BSetting,
        )

        return self.properties.get("b2bCollaborationInbound", CrossTenantAccessPolicyB2BSetting())

    @property
    def b2b_collaboration_outbound(self) -> CrossTenantAccessPolicyB2BSetting:
        """Gets the b2bCollaborationOutbound property"""
        from office365.directory.policies.crosstenant.b2_b_setting import (
            CrossTenantAccessPolicyB2BSetting,
        )

        return self.properties.get("b2bCollaborationOutbound", CrossTenantAccessPolicyB2BSetting())

    @property
    def b2b_direct_connect_inbound(self) -> CrossTenantAccessPolicyB2BSetting:
        """Gets the b2bDirectConnectInbound property"""
        from office365.directory.policies.crosstenant.b2_b_setting import (
            CrossTenantAccessPolicyB2BSetting,
        )

        return self.properties.get("b2bDirectConnectInbound", CrossTenantAccessPolicyB2BSetting())

    @property
    def b2b_direct_connect_outbound(self) -> CrossTenantAccessPolicyB2BSetting:
        """Gets the b2bDirectConnectOutbound property"""
        from office365.directory.policies.crosstenant.b2_b_setting import (
            CrossTenantAccessPolicyB2BSetting,
        )

        return self.properties.get("b2bDirectConnectOutbound", CrossTenantAccessPolicyB2BSetting())

    @property
    def inbound_trust(self) -> CrossTenantAccessPolicyInboundTrust:
        """Gets the inboundTrust property"""
        from office365.directory.policies.crosstenant.inbound_trust import (
            CrossTenantAccessPolicyInboundTrust,
        )

        return self.properties.get("inboundTrust", CrossTenantAccessPolicyInboundTrust())

    @property
    def template_application_level(self) -> TemplateApplicationLevel:
        """Gets the templateApplicationLevel property"""
        from office365.directory.applications.templateapplicationlevel import (
            TemplateApplicationLevel,
        )

        return self.properties.get("templateApplicationLevel", TemplateApplicationLevel.none)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MultiTenantOrganizationPartnerConfigurationTemplate"
