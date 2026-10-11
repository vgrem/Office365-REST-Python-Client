from __future__ import annotations

from enum import Enum


class ServiceSource(Enum):
    unknown = "0"
    microsoftDefenderForEndpoint = "1"
    microsoftDefenderForIdentity = "2"
    microsoftDefenderForCloudApps = "4"
    microsoftDefenderForOffice365 = "8"
    microsoft365Defender = "16"
    azureAdIdentityProtection = "32"
    microsoftAppGovernance = "64"
    dataLossPrevention = "128"
    unknownFutureValue = "255"
    microsoftDefenderForCloud = "256"
    microsoftSentinel = "512"
    microsoftInsiderRiskManagement = "1024"
    microsoftThreatIntelligence = "2048"
    microsoftSecurityForAI = "4096"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ServiceSource"
