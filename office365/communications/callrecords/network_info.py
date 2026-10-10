from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.callrecords.network_connection_type import (
    NetworkConnectionType,
)
from office365.communications.callrecords.network_transport_protocol import (
    NetworkTransportProtocol,
)
from office365.communications.callrecords.trace_route_hop import TraceRouteHop
from office365.communications.callrecords.wifi_band import WifiBand
from office365.communications.callrecords.wifi_radio_type import WifiRadioType
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class NetworkInfo(ClientValue):
    bandwidthLowEventRatio: float | None = None
    basicServiceSetIdentifier: str | None = None
    connectionType: NetworkConnectionType = NetworkConnectionType.unknown
    delayEventRatio: float | None = None
    dnsSuffix: str | None = None
    ipAddress: str | None = None
    linkSpeed: int | None = None
    macAddress: str | None = None
    networkTransportProtocol: NetworkTransportProtocol = NetworkTransportProtocol.unknown
    port: int | None = None
    receivedQualityEventRatio: float | None = None
    reflexiveIPAddress: str | None = None
    relayIPAddress: str | None = None
    relayPort: int | None = None
    sentQualityEventRatio: float | None = None
    subnet: str | None = None
    traceRouteHops: ClientValueCollection[TraceRouteHop] = field(
        default_factory=lambda: ClientValueCollection(TraceRouteHop)
    )
    wifiBatteryCharge: int | None = None
    wifiChannel: int | None = None
    wifiMicrosoftDriver: str | None = None
    wifiMicrosoftDriverVersion: str | None = None
    wifiSignalStrength: int | None = None
    wifiVendorDriver: str | None = None
    wifiVendorDriverVersion: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.NetworkInfo"

    wifiBand: WifiBand = WifiBand.unknown

    wifiRadioType: WifiRadioType = WifiRadioType.unknown
