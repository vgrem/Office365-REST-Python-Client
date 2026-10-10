from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from datetime import timedelta


@dataclass
class TeleconferenceDeviceMediaQuality(ClientValue):
    averageInboundJitter: timedelta | None = None
    averageInboundPacketLossRateInPercentage: float | None = None
    averageInboundRoundTripDelay: timedelta | None = None
    averageOutboundJitter: timedelta | None = None
    averageOutboundPacketLossRateInPercentage: float | None = None
    averageOutboundRoundTripDelay: timedelta | None = None
    channelIndex: int | None = None
    inboundPackets: int | None = None
    localIPAddress: str | None = None
    localPort: int | None = None
    maximumInboundJitter: timedelta | None = None
    maximumInboundPacketLossRateInPercentage: float | None = None
    maximumInboundRoundTripDelay: timedelta | None = None
    maximumOutboundJitter: timedelta | None = None
    maximumOutboundPacketLossRateInPercentage: float | None = None
    maximumOutboundRoundTripDelay: timedelta | None = None
    mediaDuration: timedelta | None = None
    networkLinkSpeedInBytes: int | None = None
    outboundPackets: int | None = None
    remoteIPAddress: str | None = None
    remotePort: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TeleconferenceDeviceMediaQuality"
