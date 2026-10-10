from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.detonation_details import DetonationDetails
from office365.runtime.client_value import ClientValue


@dataclass
class AnalyzedEmailAttachment(ClientValue):
    fileExtension: str | None = None
    fileName: str | None = None
    fileSize: int | None = None
    fileType: str | None = None
    malwareFamily: str | None = None
    sha256: str | None = None
    tenantAllowBlockListDetailInfo: str | None = None
    detonationDetails: DetonationDetails = field(default_factory=DetonationDetails)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmailAttachment"
