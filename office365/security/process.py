from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.intune.devices.management.process_integrity_level import ProcessIntegrityLevel
from office365.runtime.client_value import ClientValue
from office365.security.file_hash import FileHash


@dataclass
class Process(ClientValue):
    accountName: str | None = None
    commandLine: str | None = None
    createdDateTime: datetime | None = None
    fileHash: FileHash = field(default_factory=FileHash)
    integrityLevel: ProcessIntegrityLevel = ProcessIntegrityLevel.unknown
    isElevated: bool | None = None
    name: str | None = None
    parentProcessCreatedDateTime: datetime | None = None
    parentProcessId: int | None = None
    parentProcessName: str | None = None
    path: str | None = None
    processId: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Process"
