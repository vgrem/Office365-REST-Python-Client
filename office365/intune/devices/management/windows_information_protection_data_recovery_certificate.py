from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class WindowsInformationProtectionDataRecoveryCertificate(ClientValue):
    certificate: bytes | None = None
    description: str | None = None
    expirationDateTime: datetime | None = None
    subjectName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsInformationProtectionDataRecoveryCertificate"
