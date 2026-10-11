from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.policies.crosstenant.app_service_connect_setting import (
        CrossTenantAccessPolicyAppServiceConnectSetting,
    )
    from office365.directory.policies.crosstenant.b2_b_setting import (
        CrossTenantAccessPolicyB2BSetting,
    )
    from office365.directory.policies.crosstenant.inbound_trust import (
        CrossTenantAccessPolicyInboundTrust,
    )
    from office365.directory.policies.crosstenant.m365_collaboration_inbound_setting import (
        CrossTenantAccessPolicyM365CollaborationInboundSetting,
    )
    from office365.directory.policies.crosstenant.m365_collaboration_outbound_setting import (
        CrossTenantAccessPolicyM365CollaborationOutboundSetting,
    )
    from office365.directory.policies.crosstenant.tenant_restrictions import (
        CrossTenantAccessPolicyTenantRestrictions,
    )
    from office365.directory.policies.default_invitation_redemption_identity_provider_configuration import (
        DefaultInvitationRedemptionIdentityProviderConfiguration,
    )
    from office365.directory.policies.inbound_outbound_policy_configuration import (
        InboundOutboundPolicyConfiguration,
    )
    from office365.intune.devices.management.m365_capability_base import M365CapabilityBase


class CrossTenantAccessPolicyConfigurationDefault(Entity):
    @property
    def app_service_connect_inbound(self) -> CrossTenantAccessPolicyAppServiceConnectSetting:
        """Gets the appServiceConnectInbound property"""
        from office365.directory.policies.crosstenant.app_service_connect_setting import (
            CrossTenantAccessPolicyAppServiceConnectSetting,
        )

        return self.properties.get("appServiceConnectInbound", CrossTenantAccessPolicyAppServiceConnectSetting())

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
    def invitation_redemption_identity_provider_configuration(
        self,
    ) -> DefaultInvitationRedemptionIdentityProviderConfiguration:
        """Gets the invitationRedemptionIdentityProviderConfiguration property"""
        from office365.directory.policies.default_invitation_redemption_identity_provider_configuration import (
            DefaultInvitationRedemptionIdentityProviderConfiguration,
        )

        return self.properties.get(
            "invitationRedemptionIdentityProviderConfiguration",
            DefaultInvitationRedemptionIdentityProviderConfiguration(),
        )

    @property
    def is_service_default(self) -> Optional[bool]:
        """Gets the isServiceDefault property"""
        return self.properties.get("isServiceDefault", None)

    @property
    def m365_collaboration_inbound(self) -> CrossTenantAccessPolicyM365CollaborationInboundSetting:
        """Gets the m365CollaborationInbound property"""
        from office365.directory.policies.crosstenant.m365_collaboration_inbound_setting import (
            CrossTenantAccessPolicyM365CollaborationInboundSetting,
        )

        return self.properties.get("m365CollaborationInbound", CrossTenantAccessPolicyM365CollaborationInboundSetting())

    @property
    def m365_collaboration_outbound(self) -> CrossTenantAccessPolicyM365CollaborationOutboundSetting:
        """Gets the m365CollaborationOutbound property"""
        from office365.directory.policies.crosstenant.m365_collaboration_outbound_setting import (
            CrossTenantAccessPolicyM365CollaborationOutboundSetting,
        )

        return self.properties.get(
            "m365CollaborationOutbound", CrossTenantAccessPolicyM365CollaborationOutboundSetting()
        )

    @property
    def tenant_restrictions(self) -> CrossTenantAccessPolicyTenantRestrictions:
        """Gets the tenantRestrictions property"""
        from office365.directory.policies.crosstenant.tenant_restrictions import (
            CrossTenantAccessPolicyTenantRestrictions,
        )

        return self.properties.get("tenantRestrictions", CrossTenantAccessPolicyTenantRestrictions())

    @property
    def m365_capabilities(self) -> EntityCollection[M365CapabilityBase]:
        """Gets the m365Capabilities property"""
        from office365.intune.devices.management.m365_capability_base import M365CapabilityBase

        return self.properties.get(
            "m365Capabilities",
            EntityCollection[M365CapabilityBase](
                self.context, M365CapabilityBase, ResourcePath("m365Capabilities", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CrossTenantAccessPolicyConfigurationDefault"
