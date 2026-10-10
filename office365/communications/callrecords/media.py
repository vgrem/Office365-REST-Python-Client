from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.callrecords.device_info import DeviceInfo
from office365.communications.callrecords.media_stream import MediaStream
from office365.communications.callrecords.network_info import NetworkInfo
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class Media(ClientValue):
    calleeDevice: DeviceInfo = field(default_factory=DeviceInfo)
    calleeNetwork: NetworkInfo = field(default_factory=NetworkInfo)
    callerDevice: DeviceInfo = field(default_factory=DeviceInfo)
    callerNetwork: NetworkInfo = field(default_factory=NetworkInfo)
    label: str | None = None
    streams: ClientValueCollection[MediaStream] = field(default_factory=lambda: ClientValueCollection(MediaStream))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.Media"
