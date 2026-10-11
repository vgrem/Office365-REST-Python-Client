from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.mobileapps.mobile_app_identifier import (
    MobileAppIdentifier,
)
from office365.runtime.client_value import ClientValue


@dataclass
class ManagedAppPolicyDeploymentSummaryPerApp(ClientValue):
    configurationAppliedUserCount: int | None = None
    mobileAppIdentifier: MobileAppIdentifier = field(default_factory=MobileAppIdentifier)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedAppPolicyDeploymentSummaryPerApp"
