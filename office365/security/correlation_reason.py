from __future__ import annotations

from enum import Enum


class CorrelationReason(Enum):
    repeatedAlertOccurrence = "1"
    sameGeography = "2"
    similarArtifacts = "4"
    sameTargetedAsset = "8"
    sameNetworkSegment = "16"
    eventSequence = "32"
    timeFrame = "64"
    sameThreatSource = "128"
    similarTTPsOrBehavior = "256"
    sameActor = "512"
    sameCampaign = "1024"
    sharedIndicators = "2048"
    sameAsset = "4096"
    networkProximity = "8192"
    eventCasualSequence = "16384"
    temporalProximity = "32768"
    lateralMovementPath = "65536"
    unknownFutureValue = "131072"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CorrelationReason"
