from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.file_hash import FileHash


@dataclass
class FileSecurityState(ClientValue):
    """Contains information about the file (not process) related to the alert."""

    fileHash: FileHash = field(default_factory=FileHash)

    name: str | None = None

    path: str | None = None

    riskScore: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.FileSecurityState"
