from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection
from office365.security.alerts.azure_resource_evidence import AzureResourceEvidence


@dataclass
class SasTokenEvidence(ClientValue):
    allowedIpAddresses: str | None = None
    allowedResourceTypes: StringCollection = field(default_factory=StringCollection)
    allowedServices: StringCollection = field(default_factory=StringCollection)
    expiryDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    permissions: StringCollection = field(default_factory=StringCollection)
    protocol: str | None = None
    signatureHash: str | None = None
    signedWith: str | None = None
    startDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    storageResource: AzureResourceEvidence = field(default_factory=AzureResourceEvidence)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.SasTokenEvidence"
