from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.security.alerts.azure_resource_evidence import AzureResourceEvidence
from office365.security.alerts.iotdeviceimportancetype import IoTDeviceImportanceType
from office365.security.ip_evidence import IpEvidence
from office365.security.nic_evidence import NicEvidence
from office365.security.url_evidence import UrlEvidence


@dataclass
class IoTDeviceEvidence(ClientValue):
    deviceId: str | None = None
    deviceName: str | None = None
    devicePageLink: str | None = None
    deviceSubType: str | None = None
    deviceType: str | None = None
    importance: IoTDeviceImportanceType = IoTDeviceImportanceType.unknown
    ioTHub: AzureResourceEvidence = field(default_factory=AzureResourceEvidence)
    ioTSecurityAgentId: str | None = None
    ipAddress: IpEvidence = field(default_factory=IpEvidence)
    isAuthorized: bool | None = None
    isProgramming: bool | None = None
    isScanner: bool | None = None
    macAddress: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    operatingSystem: str | None = None
    owners: StringCollection = field(default_factory=StringCollection)
    protocols: StringCollection = field(default_factory=StringCollection)
    purdueLayer: str | None = None
    sensor: str | None = None
    serialNumber: str | None = None
    site: str | None = None
    source: str | None = None
    zone: str | None = None
    nics: ClientValueCollection[NicEvidence] = field(default_factory=lambda: ClientValueCollection(NicEvidence))
    sourceRef: UrlEvidence = field(default_factory=UrlEvidence)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IoTDeviceEvidence"
