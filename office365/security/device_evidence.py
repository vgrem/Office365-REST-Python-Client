from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.intune.devices.healthstatus import DeviceHealthStatus
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.security.alerts.defenderavstatus import DefenderAvStatus
from office365.security.logged_on_user import LoggedOnUser
from office365.security.onboarding_status import OnboardingStatus
from office365.security.resource_access_event import ResourceAccessEvent
from office365.security.riskscore import DeviceRiskScore
from office365.security.vm_metadata import VmMetadata


@dataclass
class DeviceEvidence(ClientValue):
    azureAdDeviceId: str | None = None
    defenderAvStatus: DefenderAvStatus = DefenderAvStatus.notReporting
    deviceDnsName: str | None = None
    dnsDomain: str | None = None
    firstSeenDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    healthStatus: DeviceHealthStatus = DeviceHealthStatus.active
    hostName: str | None = None
    ipInterfaces: StringCollection = field(default_factory=StringCollection)
    lastExternalIpAddress: str | None = None
    lastIpAddress: str | None = None
    mdeDeviceId: str | None = None
    ntDomain: str | None = None
    osBuild: int | None = None
    osPlatform: str | None = None
    rbacGroupId: int | None = None
    rbacGroupName: str | None = None
    riskScore: DeviceRiskScore = DeviceRiskScore.none
    version: str | None = None
    loggedOnUsers: ClientValueCollection[LoggedOnUser] = field(
        default_factory=lambda: ClientValueCollection(LoggedOnUser)
    )
    resourceAccessEvents: ClientValueCollection[ResourceAccessEvent] = field(
        default_factory=lambda: ClientValueCollection(ResourceAccessEvent)
    )
    vmMetadata: VmMetadata = field(default_factory=VmMetadata)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DeviceEvidence"

    onboardingStatus: OnboardingStatus = OnboardingStatus.insufficientInfo
