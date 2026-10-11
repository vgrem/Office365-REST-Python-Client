from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.alerts.detectionstatus import DetectionStatus
from office365.security.file_details import FileDetails


@dataclass
class FileEvidence(ClientValue):
    detectionStatus: DetectionStatus = DetectionStatus.detected
    fileDetails: FileDetails = field(default_factory=FileDetails)
    mdeDeviceId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.FileEvidence"
