from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class DeviceHealthAttestationState(ClientValue):
    attestationIdentityKey: str | None = None
    bitLockerStatus: str | None = None
    bootAppSecurityVersion: str | None = None
    bootDebugging: str | None = None
    bootManagerSecurityVersion: str | None = None
    bootManagerVersion: str | None = None
    bootRevisionListInfo: str | None = None
    codeIntegrity: str | None = None
    codeIntegrityCheckVersion: str | None = None
    codeIntegrityPolicy: str | None = None
    contentNamespaceUrl: str | None = None
    contentVersion: str | None = None
    dataExcutionPolicy: str | None = None
    deviceHealthAttestationStatus: str | None = None
    earlyLaunchAntiMalwareDriverProtection: str | None = None
    healthAttestationSupportedStatus: str | None = None
    healthStatusMismatchInfo: str | None = None
    issuedDateTime: datetime | None = None
    lastUpdateDateTime: str | None = None
    operatingSystemKernelDebugging: str | None = None
    operatingSystemRevListInfo: str | None = None
    pcr0: str | None = None
    pcrHashAlgorithm: str | None = None
    resetCount: int | None = None
    restartCount: int | None = None
    safeMode: str | None = None
    secureBoot: str | None = None
    secureBootConfigurationPolicyFingerPrint: str | None = None
    testSigning: str | None = None
    tpmVersion: str | None = None
    virtualSecureMode: str | None = None
    windowsPE: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceHealthAttestationState"
