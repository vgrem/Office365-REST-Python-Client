from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ReportFileMetadata(ClientValue):
    downloadUrl: str | None = None
    fileName: str | None = None
    size: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ReportFileMetadata"
