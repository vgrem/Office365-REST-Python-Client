from __future__ import annotations

from dataclasses import field
from datetime import datetime

from office365.security.alerts.detectionstatus import DetectionStatus
from office365.security.alerts.evidence import AlertEvidence
from office365.security.file_details import FileDetails
from office365.security.user_account import UserAccount


class ProcessEvidence(AlertEvidence):
    detectionStatus: DetectionStatus = DetectionStatus.detected
    imageFile: FileDetails = field(default_factory=FileDetails)
    mdeDeviceId: str | None = None
    parentProcessCreationDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    parentProcessId: int | None = None
    parentProcessImageFile: FileDetails = field(default_factory=FileDetails)
    processCommandLine: str | None = None
    processCreationDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    processId: int | None = None
    userAccount: UserAccount = field(default_factory=UserAccount)
    "Represents a process that is reported in the alert as evidence."

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ProcessEvidence"
