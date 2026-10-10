from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.windows.statemanagementsetting import (
    StateManagementSetting,
)
from office365.runtime.client_value import ClientValue


@dataclass
class WindowsFirewallNetworkProfile(ClientValue):
    authorizedApplicationRulesFromGroupPolicyMerged: bool | None = None
    connectionSecurityRulesFromGroupPolicyMerged: bool | None = None
    firewallEnabled: StateManagementSetting = StateManagementSetting.notConfigured
    globalPortRulesFromGroupPolicyMerged: bool | None = None
    inboundConnectionsBlocked: bool | None = None
    inboundNotificationsBlocked: bool | None = None
    incomingTrafficBlocked: bool | None = None
    outboundConnectionsBlocked: bool | None = None
    policyRulesFromGroupPolicyMerged: bool | None = None
    securedPacketExemptionAllowed: bool | None = None
    stealthModeBlocked: bool | None = None
    unicastResponsesToMulticastBroadcastsBlocked: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsFirewallNetworkProfile"
